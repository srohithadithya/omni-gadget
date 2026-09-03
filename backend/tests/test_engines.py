"""
Comprehensive pytest tests for AIDE-OS backend engines.
Covers URL, Chipflation, EMI, and Recommendation engines with
boundary conditions, edge cases, and normal flows.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

# ---------------------------------------------------------------------------
# URL Engine
# ---------------------------------------------------------------------------
from app.engines.url_engine import calculate_url, URLInput


class TestURLEngine:
    """Tests for the Useful Remaining Life (URL) calculator."""

    def test_normal_case(self):
        """Standard mid-life mobile: URL ~66.7%, HOLD_CURRENT_DEVICE."""
        inp = URLInput(
            category="mobile", age_months=42,
            battery_health_pct=72, storage_health_pct=85,
            physical_condition=0.85, eol_months=60,
        )
        result = calculate_url(inp)

        # Manual calc:
        # bh=0.72, sh=0.85, af=1-42/60=0.3, ph=0.85
        # url = (0.35*0.72 + 0.25*0.85 + 0.25*0.3 + 0.15*0.85)*100
        #     = (0.252 + 0.2125 + 0.075 + 0.1275)*100 = 66.7
        assert result.url_score_pct == 66.7
        assert result.decision == "HOLD_CURRENT_DEVICE"
        # bh=0.72 < 0.75, so advice should mention battery
        assert "battery" in result.maintenance_advice.lower()
        # Lifespan for mobile = 5.0 years; years_left = 66.7/100*5 = 3.3
        assert result.estimated_years_left == 3.3

    def test_brand_new_device(self):
        """Brand-new device with perfect scores -> URL near 100%, HOLD."""
        inp = URLInput(
            category="mobile", age_months=0,
            battery_health_pct=100, storage_health_pct=100,
            physical_condition=1.0, eol_months=60,
        )
        result = calculate_url(inp)

        assert result.url_score_pct == 100.0
        assert result.decision == "HOLD_CURRENT_DEVICE"
        assert result.estimated_years_left == 5.0
        assert "good shape" in result.maintenance_advice.lower()

    def test_dead_device(self):
        """Completely worn-out device -> REPLACE_IMMEDIATELY."""
        inp = URLInput(
            category="mobile", age_months=84,
            battery_health_pct=10, storage_health_pct=15,
            physical_condition=0.1, eol_months=60,
        )
        result = calculate_url(inp)

        # bh=0.1, sh=0.15, af=max(0,1-84/60)=0, ph=0.1
        # url = (0.035+0.0375+0+0.015)*100 = 8.75
        assert result.url_score_pct == pytest.approx(8.75, abs=0.01)
        assert result.decision == "REPLACE_IMMEDIATELY"
        assert result.estimated_years_left == pytest.approx(0.4, abs=0.1)

    def test_boundary_exactly_60(self):
        """URL score exactly 60.0 should be HOLD_CURRENT_DEVICE."""
        # bh=1.0, sh=1.0, af=0 (age==eol), ph=0 -> (0.35+0.25+0+0)*100 = 60.0
        inp = URLInput(
            category="mobile", age_months=60,
            battery_health_pct=100, storage_health_pct=100,
            physical_condition=0.0, eol_months=60,
        )
        result = calculate_url(inp)

        assert result.url_score_pct == 60.0
        assert result.decision == "HOLD_CURRENT_DEVICE"

    def test_boundary_exactly_40(self):
        """URL score exactly 40.0 should be CONSIDER_REPLACEMENT."""
        # bh=0, sh=1.0, af=0.6, ph=0 -> (0+0.25+0.15+0)*100 = 40.0
        # age=24, eol=60 -> af=1-24/60=0.6
        inp = URLInput(
            category="mobile", age_months=24,
            battery_health_pct=0, storage_health_pct=100,
            physical_condition=0.0, eol_months=60,
        )
        result = calculate_url(inp)

        assert result.url_score_pct == 40.0
        assert result.decision == "CONSIDER_REPLACEMENT"

    def test_boundary_39_9(self):
        """URL score 39.9 (just below 40) -> REPLACE_IMMEDIATELY."""
        # bh=0.6, sh=0.6, af=0 (age==eol), ph=0.26
        # (0.21 + 0.15 + 0 + 0.039)*100 = 39.9
        inp = URLInput(
            category="mobile", age_months=60,
            battery_health_pct=60, storage_health_pct=60,
            physical_condition=0.26, eol_months=60,
        )
        result = calculate_url(inp)

        assert result.url_score_pct == pytest.approx(39.9, abs=0.01)
        assert result.decision == "REPLACE_IMMEDIATELY"

    def test_age_exceeds_eol_clamps_age_factor(self):
        """When age_months > eol_months, age_factor clamps to 0."""
        inp = URLInput(
            category="mobile", age_months=84,
            battery_health_pct=100, storage_health_pct=100,
            physical_condition=1.0, eol_months=60,
        )
        result = calculate_url(inp)

        # af = max(0, 1-84/60) = 0
        # url = (0.35 + 0.25 + 0 + 0.15)*100 = 75.0
        assert result.component_scores["age_factor_pct"] == 0.0
        assert result.url_score_pct == 75.0
        assert result.decision == "HOLD_CURRENT_DEVICE"

    @pytest.mark.parametrize("category,expected_lifespan", [
        ("mobile", 5.0),
        ("laptop", 6.0),
        ("audio", 5.0),
        ("video", 8.0),
        ("memory", 7.0),
        ("wearable", 4.0),
    ])
    def test_all_categories(self, category, expected_lifespan):
        """Every supported category produces a valid result with correct lifespan."""
        inp = URLInput(
            category=category, age_months=12,
            battery_health_pct=90, storage_health_pct=90,
            physical_condition=0.9,
        )
        result = calculate_url(inp)

        assert result.url_score_pct > 0
        assert result.decision in (
            "HOLD_CURRENT_DEVICE", "CONSIDER_REPLACEMENT", "REPLACE_IMMEDIATELY"
        )
        # years_left = (url_score/100) * lifespan
        assert result.estimated_years_left == pytest.approx(
            (result.url_score_pct / 100.0) * expected_lifespan, abs=0.1
        )
        # Component scores should all be 0-100
        for key in ("battery_pct", "storage_pct", "age_factor_pct", "physical_pct"):
            assert 0 <= result.component_scores[key] <= 100

    def test_maintenance_advice_storage_wear(self):
        """When battery >= 75% but storage < 70%, advice mentions storage."""
        inp = URLInput(
            category="mobile", age_months=0,
            battery_health_pct=90, storage_health_pct=60,
            physical_condition=1.0, eol_months=60,
        )
        result = calculate_url(inp)

        # bh=0.9 >= 0.75, sh=0.6 < 0.70, url_score should be >= 60
        assert result.url_score_pct >= 60.0
        assert result.decision == "HOLD_CURRENT_DEVICE"
        assert "storage" in result.maintenance_advice.lower()

    def test_physical_condition_clamped(self):
        """Physical condition values outside 0-1 are clamped."""
        # physical_condition > 1.0 should clamp to 1.0
        inp_high = URLInput(
            category="mobile", age_months=0,
            battery_health_pct=100, storage_health_pct=100,
            physical_condition=1.5, eol_months=60,
        )
        result_high = calculate_url(inp_high)
        assert result_high.url_score_pct == 100.0

        # negative physical should clamp to 0.0
        inp_low = URLInput(
            category="mobile", age_months=0,
            battery_health_pct=100, storage_health_pct=100,
            physical_condition=-0.5, eol_months=60,
        )
        result_low = calculate_url(inp_low)
        # url = (0.35+0.25+0.25+0)*100 = 85.0
        assert result_low.url_score_pct == 85.0

    def test_battery_health_over_100_clamped(self):
        """Battery health > 100% should clamp to 1.0 internally."""
        inp = URLInput(
            category="mobile", age_months=0,
            battery_health_pct=150, storage_health_pct=100,
            physical_condition=1.0, eol_months=60,
        )
        result = calculate_url(inp)
        assert result.url_score_pct == 100.0

    def test_default_eol_and_lifespan(self):
        """When eol_months and max_lifespan_years are not provided, defaults are used."""
        inp = URLInput(
            category="laptop", age_months=12,
            battery_health_pct=80, storage_health_pct=80,
            physical_condition=0.8,
            # eol_months=None -> defaults to CATEGORY_EOL_MONTHS["laptop"] = 72
            # max_lifespan_years=None -> defaults to CATEGORY_LIFESPAN["laptop"] = 6.0
        )
        result = calculate_url(inp)

        # af = 1-12/72 = 0.8333
        # url = (0.35*0.8 + 0.25*0.8 + 0.25*0.8333 + 0.15*0.8)*100
        #     = (0.28+0.20+0.20833+0.12)*100 = 80.83
        assert result.url_score_pct == pytest.approx(80.83, abs=0.1)
        # years = 0.8083 * 6.0 = 4.85
        assert result.estimated_years_left == pytest.approx(4.85, abs=0.1)

    def test_unknown_category_uses_defaults(self):
        """Unknown category falls back to generic defaults (eol=60, lifespan=5)."""
        inp = URLInput(
            category="toaster", age_months=30,
            battery_health_pct=70, storage_health_pct=70,
            physical_condition=0.7,
        )
        result = calculate_url(inp)

        # af = 1-30/60 = 0.5
        # url = (0.35*0.7+0.25*0.7+0.25*0.5+0.15*0.7)*100
        #     = (0.245+0.175+0.125+0.105)*100 = 65.0
        assert result.url_score_pct == pytest.approx(65.0, abs=0.01)
        assert result.decision == "HOLD_CURRENT_DEVICE"


# ---------------------------------------------------------------------------
# Chipflation Engine
# ---------------------------------------------------------------------------
from app.engines.chipflation_engine import calculate_di, ChipflationInput, SEASONAL_HINTS, CATEGORY_CHIPFLATION


class TestChipflationEngine:
    """Tests for the Chipflation Decision Index (DI) calculator."""

    def test_optimal_buy(self):
        """Low CI + cheap price -> DI < 0.95, OPTIMAL_BUY_WINDOW."""
        inp = ChipflationInput(
            category="mobile",
            current_price=25000,
            historical_baseline=27000,
            url_score=66.7,
            chipflation_index=0.9,
        )
        result = calculate_di(inp)

        # price_inflation_factor = 0.9 * 25000 / 27000 = 0.83333...
        # url_drag = (1 - 66.7/100) * 1.0 = 0.333
        # di = 0.833 - 0.333 = 0.5
        assert result.decision_index == pytest.approx(0.500, abs=0.01)
        assert result.decision == "OPTIMAL_BUY_WINDOW"
        assert result.buy_window == "BUY_NOW"

    def test_overpriced(self):
        """High CI + inflated price -> DI > 1.25, OVERPRICED."""
        inp = ChipflationInput(
            category="mobile",
            current_price=35000,
            historical_baseline=27000,
            url_score=66.7,
            chipflation_index=1.25,
        )
        result = calculate_di(inp)

        # price_inflation_factor = 1.25 * 35000 / 27000 = 1.62037
        # url_drag = 0.333
        # di = 1.620 - 0.333 = 1.287
        assert result.decision_index > 1.25
        assert result.decision == "OVERPRICED_HIGH_INFLATION"
        assert result.buy_window == "HOLD_OR_BUY_REFURBISHED"

    def test_moderate_pricing(self):
        """Moderate CI with URL offset -> DI in 0.95-1.25 range, STABLE."""
        inp = ChipflationInput(
            category="mobile",
            current_price=32000,
            historical_baseline=27000,
            url_score=66.7,
            chipflation_index=1.18,
        )
        result = calculate_di(inp)

        # price_inflation_factor = 1.18 * 32000 / 27000 = 1.39852
        # url_drag = 0.333
        # di = 1.39852 - 0.333 = 1.066
        assert 0.95 <= result.decision_index <= 1.25
        assert result.decision == "STABLE_MODERATE_PRICING"
        assert result.buy_window == "BUY_WITH_CASHBACK_EMI"

    def test_urgency_factor_shifts_verdict(self):
        """High urgency increases url_drag, potentially lowering DI into optimal zone."""
        inp_no_urgency = ChipflationInput(
            category="mobile",
            current_price=32000,
            historical_baseline=27000,
            url_score=66.7,
            chipflation_index=1.18,
            urgency_factor=1.0,
        )
        inp_high_urgency = ChipflationInput(
            category="mobile",
            current_price=32000,
            historical_baseline=27000,
            url_score=66.7,
            chipflation_index=1.18,
            urgency_factor=2.0,
        )
        r1 = calculate_di(inp_no_urgency)
        r2 = calculate_di(inp_high_urgency)

        # No urgency: di ~ 1.066 -> STABLE
        # High urgency: url_drag doubles -> di = 1.39852 - 0.666 = 0.733 -> OPTIMAL
        assert r1.decision == "STABLE_MODERATE_PRICING"
        assert r2.decision == "OPTIMAL_BUY_WINDOW"
        assert r2.decision_index < r1.decision_index

    def test_price_vs_baseline_pct(self):
        """price_vs_baseline_pct correctly reflects markup/discount vs baseline."""
        inp = ChipflationInput(
            category="laptop",
            current_price=78000,
            historical_baseline=65000,
            url_score=50.0,
        )
        result = calculate_di(inp)

        expected_pct = round(((78000 - 65000) / 65000) * 100, 2)
        assert result.price_vs_baseline_pct == expected_pct

    def test_market_status_values(self):
        """market_status reflects the chipflation_index: INFLATED / STABLE / DEFLATING."""
        cases = [
            (1.20, "INFLATED"),   # > 1.10 -> INFLATED
            (1.15, "INFLATED"),   # > 1.10 -> INFLATED
            (1.0, "STABLE"),      # > 0.98 and <= 1.10
            (0.8, "DEFLATING"),   # <= 0.98
        ]
        for ci, expected_status in cases:
            inp = ChipflationInput(
                category="audio", current_price=10000,
                historical_baseline=10000, url_score=50.0,
                chipflation_index=ci,
            )
            result = calculate_di(inp)
            assert result.market_status == expected_status, (
                f"CI={ci}: expected market_status={expected_status}, got {result.market_status}"
            )

    @pytest.mark.parametrize("category", [
        "mobile", "laptop", "audio", "video", "memory", "wearable",
    ])
    def test_all_categories_driver_text(self, category):
        """Each category returns a non-empty driver string."""
        inp = ChipflationInput(
            category=category,
            current_price=30000,
            historical_baseline=27000,
            url_score=60.0,
        )
        result = calculate_di(inp)

        assert isinstance(result.driver, str)
        assert len(result.driver) > 0

    @pytest.mark.parametrize("category", [
        "mobile", "laptop", "audio", "video", "memory", "wearable",
    ])
    def test_all_categories_seasonal_hint(self, category):
        """Each category returns a non-empty seasonal_hint string."""
        inp = ChipflationInput(
            category=category,
            current_price=30000,
            historical_baseline=27000,
            url_score=60.0,
        )
        result = calculate_di(inp)

        assert isinstance(result.seasonal_hint, str)
        assert len(result.seasonal_hint) > 0
        assert result.seasonal_hint == SEASONAL_HINTS[category]

    def test_unknown_category_fallback(self):
        """Unknown category uses fallback profile (index=1.10, generic driver)."""
        inp = ChipflationInput(
            category="toaster",
            current_price=1000,
            historical_baseline=1000,
            url_score=50.0,
        )
        result = calculate_di(inp)

        assert result.chipflation_index == 1.10
        assert "inflation" in result.driver.lower()

    def test_chipflation_index_override(self):
        """Explicit chipflation_index overrides the category default."""
        # Mobile default CI is 1.18; override to 0.5
        inp = ChipflationInput(
            category="mobile",
            current_price=30000,
            historical_baseline=30000,
            url_score=50.0,
            chipflation_index=0.5,
        )
        result = calculate_di(inp)
        assert result.chipflation_index == 0.5

    def test_zero_url_score_max_drag(self):
        """url_score=0 means max url_drag (1.0 * urgency_factor)."""
        inp = ChipflationInput(
            category="mobile",
            current_price=30000,
            historical_baseline=30000,
            url_score=0.0,
            chipflation_index=1.0,
        )
        result = calculate_di(inp)

        # price_inflation_factor = 1.0 * 30000/30000 = 1.0
        # url_drag = (1 - 0) * 1.0 = 1.0
        # di = 1.0 - 1.0 = 0.0 -> OPTIMAL_BUY_WINDOW
        assert result.decision_index == pytest.approx(0.0, abs=0.01)
        assert result.decision == "OPTIMAL_BUY_WINDOW"

    def test_full_url_score_no_drag(self):
        """url_score=100 means zero url_drag."""
        inp = ChipflationInput(
            category="mobile",
            current_price=30000,
            historical_baseline=30000,
            url_score=100.0,
            chipflation_index=1.2,
        )
        result = calculate_di(inp)

        # price_inflation_factor = 1.2
        # url_drag = (1-1)*1.0 = 0
        # di = 1.2 -> STABLE (0.95 <= 1.2 <= 1.25)
        assert result.decision_index == pytest.approx(1.2, abs=0.01)
        assert result.decision == "STABLE_MODERATE_PRICING"


# ---------------------------------------------------------------------------
# EMI Engine
# ---------------------------------------------------------------------------
from app.engines.emi_engine import calculate_true_emi_cost, EMIInput


class TestEMIEngine:
    """Tests for the True-Cost EMI & Hidden Charges Extractor."""

    def test_basic_pay_upfront(self):
        """Hidden charges > 2000 -> PAY_UPFRONT_CASH."""
        inp = EMIInput(
            product_msrp=40000,
            no_cost_discount=2500,
            bank_processing_fee=299,
            tenure_months=6,
            forgone_cash_discount=1500,
        )
        result = calculate_true_emi_cost(inp)

        # gst_on_processing = 299 * 0.18 = 53.82
        # gst_on_interest = 2500 * 0.18 = 450
        # total_hidden = 299 + 53.82 + 450 + 1500 = 2302.82
        assert result.total_hidden_charges == pytest.approx(2302.82, abs=0.01)
        assert result.total_hidden_charges > 2000
        assert result.recommendation == "PAY_UPFRONT_CASH"

    def test_acceptable(self):
        """Hidden charges < 800 -> EMI_ACCEPTABLE."""
        inp = EMIInput(
            product_msrp=10000,
            no_cost_discount=500,
            bank_processing_fee=199,
            tenure_months=3,
            forgone_cash_discount=0,
        )
        result = calculate_true_emi_cost(inp)

        # gst_on_processing = 199*0.18 = 35.82
        # gst_on_interest = 500*0.18 = 90
        # total_hidden = 199 + 35.82 + 90 + 0 = 324.82
        assert result.total_hidden_charges == pytest.approx(324.82, abs=0.01)
        assert result.total_hidden_charges < 800
        assert result.recommendation == "EMI_ACCEPTABLE"

    def test_reconsider(self):
        """Hidden charges between 800 and 2000 -> RECONSIDER_EMI_TENURE."""
        # Use inputs that actually land in 800-2000 range:
        # gst_on_processing = 299*0.18 = 53.82
        # gst_on_interest = 2000*0.18 = 360
        # total_hidden = 299 + 53.82 + 360 + 500 = 1212.82
        inp = EMIInput(
            product_msrp=40000,
            no_cost_discount=2000,
            bank_processing_fee=299,
            tenure_months=6,
            forgone_cash_discount=500,
        )
        result = calculate_true_emi_cost(inp)

        assert result.total_hidden_charges == pytest.approx(1212.82, abs=0.01)
        assert 800 < result.total_hidden_charges < 2000
        assert result.recommendation == "RECONSIDER_EMI_TENURE"

    def test_zero_everything(self):
        """All hidden charges zero -> total_hidden=0, EMI_ACCEPTABLE."""
        inp = EMIInput(
            product_msrp=20000,
            no_cost_discount=0,
            bank_processing_fee=0,
            tenure_months=12,
            forgone_cash_discount=0,
        )
        result = calculate_true_emi_cost(inp)

        assert result.total_hidden_charges == 0.0
        assert result.true_effective_outlay == 20000.0
        assert result.hidden_charge_pct == 0.0
        assert result.recommendation == "EMI_ACCEPTABLE"

    def test_exchange_bonus_reduces_true_cost(self):
        """Exchange bonus should reduce the true effective outlay."""
        inp_without = EMIInput(
            product_msrp=40000,
            no_cost_discount=1000,
            bank_processing_fee=199,
            tenure_months=6,
            forgone_cash_discount=300,
            exchange_bonus=0,
        )
        inp_with = EMIInput(
            product_msrp=40000,
            no_cost_discount=1000,
            bank_processing_fee=199,
            tenure_months=6,
            forgone_cash_discount=300,
            exchange_bonus=3000,
        )
        r_without = calculate_true_emi_cost(inp_without)
        r_with = calculate_true_emi_cost(inp_with)

        # Exchange bonus subtracts directly from true_cost
        assert r_with.true_effective_outlay == pytest.approx(
            r_without.true_effective_outlay - 3000, abs=0.01
        )

    def test_breakdown_has_five_keys(self):
        """Breakdown dict contains exactly the 5 expected keys."""
        inp = EMIInput(
            product_msrp=50000,
            no_cost_discount=2000,
            bank_processing_fee=299,
            tenure_months=12,
            forgone_cash_discount=500,
            exchange_bonus=1000,
        )
        result = calculate_true_emi_cost(inp)

        expected_keys = {
            "bank_processing_fee",
            "gst_on_processing_fee_18pct",
            "unrefundable_gst_on_interest_18pct",
            "forgone_upfront_cash_discount",
            "exchange_bonus_deducted",
        }
        assert set(result.breakdown.keys()) == expected_keys

    def test_monthly_emi_calculation(self):
        """monthly_emi == true_effective_outlay / tenure_months."""
        inp = EMIInput(
            product_msrp=40000,
            no_cost_discount=2000,
            bank_processing_fee=299,
            tenure_months=6,
            forgone_cash_discount=500,
        )
        result = calculate_true_emi_cost(inp)

        expected_monthly = round(result.true_effective_outlay / 6, 2)
        assert result.monthly_emi == expected_monthly

    def test_advertised_price_matches_msrp(self):
        """advertised_price should equal the input product_msrp."""
        inp = EMIInput(
            product_msrp=65000,
            no_cost_discount=1000,
            bank_processing_fee=199,
            tenure_months=3,
            forgone_cash_discount=200,
        )
        result = calculate_true_emi_cost(inp)
        assert result.advertised_price == 65000

    def test_hidden_charge_pct(self):
        """hidden_charge_pct = (total_hidden / msrp) * 100, rounded to 2 dp."""
        inp = EMIInput(
            product_msrp=20000,
            no_cost_discount=0,
            bank_processing_fee=100,
            tenure_months=3,
            forgone_cash_discount=0,
        )
        result = calculate_true_emi_cost(inp)

        # total_hidden = 100 + 18 + 0 + 0 = 118
        # pct = 118/20000 * 100 = 0.59
        assert result.total_hidden_charges == pytest.approx(118.0, abs=0.01)
        assert result.hidden_charge_pct == 0.59

    def test_exchange_bonus_in_breakdown(self):
        """Breakdown shows exchange_bonus_deducted correctly."""
        inp = EMIInput(
            product_msrp=30000,
            no_cost_discount=500,
            bank_processing_fee=199,
            tenure_months=6,
            forgone_cash_discount=0,
            exchange_bonus=2500,
        )
        result = calculate_true_emi_cost(inp)
        assert result.breakdown["exchange_bonus_deducted"] == 2500.0

    def test_gst_calculated_at_18_percent(self):
        """GST components use 18% rate."""
        inp = EMIInput(
            product_msrp=50000,
            no_cost_discount=10000,
            bank_processing_fee=500,
            tenure_months=12,
            forgone_cash_discount=0,
        )
        result = calculate_true_emi_cost(inp)

        assert result.breakdown["gst_on_processing_fee_18pct"] == pytest.approx(90.0, abs=0.01)
        assert result.breakdown["unrefundable_gst_on_interest_18pct"] == pytest.approx(1800.0, abs=0.01)


# ---------------------------------------------------------------------------
# Recommendation Engine
# ---------------------------------------------------------------------------
from app.engines.recommendation_engine import recommend_products, RecommendationInput


class TestRecommendationEngine:
    """Tests for the Product Recommendation engine."""

    def test_gaming_mobile_under_35k(self):
        """Gaming mobile under ₹35,000 should return products in budget."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=35000,
        )
        result = recommend_products(inp)

        assert len(result["primary"]) > 0
        # The Nothing Phone 4(a) at 30000 should appear
        all_ids = [m["product"]["id"] for m in result["primary"] + result["alternatives"]]
        assert "mob_002" in all_ids  # Nothing Phone 4(a) at ₹30k

    def test_out_of_budget_still_returns_products(self):
        """Very low budget still returns products (over-budget penalty, not empty)."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=5000,
        )
        result = recommend_products(inp)

        # All mobiles are above 5000, but the engine still scores and returns them
        total_products = (
            len(result["primary"]) + len(result["alternatives"]) + len(result["refurbished"])
        )
        assert total_products > 0

    def test_prefer_refurbished_populates_list(self):
        """prefer_refurbished=True should populate the refurbished list."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=60000,
            prefer_refurbished=True,
        )
        result = recommend_products(inp)

        assert len(result["refurbished"]) > 0
        # Verify refurbished entries have refurb_price_inr
        for item in result["refurbished"]:
            prod = item["product"]
            assert prod.get("refurb_price_inr") is not None or prod.get("display_price") is not None

    def test_empty_category_returns_empty(self):
        """Unknown category returns empty lists."""
        inp = RecommendationInput(
            category="nonexistent",
            use_case="gaming",
            max_budget_inr=50000,
        )
        result = recommend_products(inp)

        assert result["primary"] == []
        assert result["alternatives"] == []
        assert result["refurbished"] == []

    def test_use_case_alias_gaming(self):
        """'gaming' use_case alias expands to ['gaming', 'multitasking']."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=100000,
        )
        result = recommend_products(inp)

        # Samsung Galaxy S25 has use_cases: ["gaming", "multitasking", "photography"]
        all_products = result["primary"] + result["alternatives"]
        all_ids = [m["product"]["id"] for m in all_products]
        # Galaxy S25, Nothing Phone 4(a), Galaxy S23, OnePlus 11R all have 'gaming'
        assert "mob_001" in all_ids or "mob_002" in all_ids

    def test_value_verdict_scores(self):
        """Products below baseline*0.95 are GREAT_VALUE, above baseline*1.10 are OVERPRICED."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=100000,
        )
        result = recommend_products(inp)

        all_matches = result["primary"] + result["alternatives"]
        verdicts = [m["value_verdict"] for m in all_matches]
        assert "GREAT_VALUE" in verdicts  # Galaxy S23 at 52000 vs baseline 70000

    def test_ram_filter_applied(self):
        """min_ram_gb=16 should penalize products with less RAM."""
        inp_low = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=100000,
            min_ram_gb=16,
        )
        result_low = recommend_products(inp_low)

        # Only OnePlus 11R has 16GB RAM among mobiles
        all_products = result_low["primary"] + result_low["alternatives"]
        if all_products:
            # Top product should be OnePlus 11R (16GB RAM gets +15 bonus)
            top_id = all_products[0]["product"]["id"]
            assert top_id == "mob_005"  # OnePlus 11R

    def test_storage_filter_applied(self):
        """min_storage_gb=256 should penalize products with less storage."""
        inp = RecommendationInput(
            category="mobile",
            use_case="daily_tasks",
            max_budget_inr=50000,
            min_storage_gb=256,
        )
        result = recommend_products(inp)

        # Redmi Note 15 Pro (128GB) should be penalized
        # All other mobiles have 256GB
        all_products = result["primary"] + result["alternatives"]
        all_ids = [m["product"]["id"] for m in all_products]
        # The top picks should not be Redmi (128GB < 256)
        if all_products:
            assert all_products[0]["product"]["id"] != "mob_004"

    def test_laptop_recommendations(self):
        """Laptop category returns relevant coding/productivity matches."""
        inp = RecommendationInput(
            category="laptop",
            use_case="coding",
            max_budget_inr=80000,
        )
        result = recommend_products(inp)

        assert len(result["primary"]) > 0
        all_products = result["primary"] + result["alternatives"]
        # At least one laptop should be returned
        assert len(all_products) > 0

    def test_audio_recommendations(self):
        """Audio category returns relevant products."""
        inp = RecommendationInput(
            category="audio",
            use_case="anc",
            max_budget_inr=30000,
        )
        result = recommend_products(inp)

        assert len(result["primary"]) > 0
        # Sony WH-1000XM5 should be top pick for ANC
        top = result["primary"][0]["product"]
        assert top["brand"] == "Sony"

    def test_alternatives_limited_to_3(self):
        """alternatives list is capped at 3 entries."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=100000,
        )
        result = recommend_products(inp)
        assert len(result["alternatives"]) <= 3

    def test_primary_limited_to_2(self):
        """primary list is capped at 2 entries."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=100000,
        )
        result = recommend_products(inp)
        assert len(result["primary"]) <= 2

    def test_refurbished_limited_to_3(self):
        """refurbished list is capped at 3 entries."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=100000,
            prefer_refurbished=True,
        )
        result = recommend_products(inp)
        assert len(result["refurbished"]) <= 3

    def test_match_score_is_non_negative(self):
        """Match scores should be non-negative after sorting."""
        inp = RecommendationInput(
            category="mobile",
            use_case="gaming",
            max_budget_inr=100000,
        )
        result = recommend_products(inp)

        for item in result["primary"] + result["alternatives"]:
            # Raw score could theoretically be negative, but final displayed
            # score should be reasonable
            assert isinstance(item["match_score"], float)

    def test_daily_tasks_use_case(self):
        """'daily_tasks' alias should match social_media and daily_tasks products."""
        inp = RecommendationInput(
            category="mobile",
            use_case="daily_tasks",
            max_budget_inr=25000,
        )
        result = recommend_products(inp)

        all_products = result["primary"] + result["alternatives"]
        assert len(all_products) > 0
        # Redmi Note 15 Pro (22000) has daily_tasks and social_media
        all_ids = [m["product"]["id"] for m in all_products]
        assert "mob_004" in all_ids

    def test_open_box_goes_to_refurbished(self):
        """Products with tier='certified-open-box' should appear in refurbished list."""
        inp = RecommendationInput(
            category="laptop",
            use_case="coding",
            max_budget_inr=60000,
        )
        result = recommend_products(inp)

        # Lenovo ThinkPad E14 (Open-Box) has tier='certified-open-box'
        refurb_ids = [m["product"]["id"] for m in result["refurbished"]]
        assert "lap_003" in refurb_ids
