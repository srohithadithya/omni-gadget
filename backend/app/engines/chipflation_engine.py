"""
Module 3: Chipflation Decision Index (DI) Engine
Buy vs Hold based on component inflation and URL score.
"""
from dataclasses import dataclass
from typing import Optional


# Static chipflation risk profiles per category (can be overridden by live data)
CATEGORY_CHIPFLATION = {
    "mobile":   {"index": 1.18, "driver": "LPDDR5X mobile RAM costs up 15–20%"},
    "laptop":   {"index": 1.22, "driver": "DDR5 SO-DIMM & PCIe Gen4 SSD costs elevated by AI data center demand"},
    "audio":    {"index": 1.03, "driver": "Bluetooth SoCs stable; minor logistics cost on neodymium drivers"},
    "video":    {"index": 1.07, "driver": "Display panel yields stable; mainboard processors slightly inflated"},
    "memory":   {"index": 1.25, "driver": "NAND flash wafer spot prices elevated due to enterprise AI server demand"},
    "wearable": {"index": 1.06, "driver": "Micro-AMOLED displays seeing minor price shifts"},
}


@dataclass
class ChipflationInput:
    category: str
    current_price: float
    historical_baseline: float
    url_score: float                     # from URL engine, 0–100
    urgency_factor: float = 1.0          # 1.0 = neutral, >1 = user needs it now
    chipflation_index: Optional[float] = None  # override; uses category default if None


@dataclass
class ChipflationResult:
    decision_index: float
    decision: str
    buy_window: str
    advice: str
    price_vs_baseline_pct: float
    chipflation_index: float
    driver: str
    market_status: str
    seasonal_hint: str


SEASONAL_HINTS = {
    "mobile":   "Best windows: Diwali / Big Billion Days (Oct–Nov), Republic Day Sale (Jan)",
    "laptop":   "Best windows: Back-to-College (Jul–Aug), Festive Sales (Oct–Nov)",
    "audio":    "Best windows: Quarterly Flash Clearance, Prime Day (Jul)",
    "video":    "Best windows: New Year Sale (Jan), Independence Day (Aug), Diwali (Oct–Nov)",
    "memory":   "DO NOT buy at full MSRP. Wait for seasonal bundle promos or price correction.",
    "wearable": "Best windows: Smartphone bundle promos, Festive Sales (Oct–Nov)",
}


def _get_profile(cat: str) -> dict:
    """Try DB first, fall back to static dict."""
    try:
        from app.db import get_chipflation_profile
        db_profile = get_chipflation_profile(cat)
        if db_profile:
            return db_profile
    except Exception:
        pass
    return CATEGORY_CHIPFLATION.get(cat, {"index": 1.10, "driver": "Moderate inflation"})


def calculate_di(inp: ChipflationInput) -> ChipflationResult:
    cat = inp.category.lower()
    profile = _get_profile(cat)
    ci = inp.chipflation_index if inp.chipflation_index is not None else profile.get("index", 1.10)
    driver = profile.get("driver", "Moderate inflation")

    # DI formula from spec
    price_inflation_factor = (ci * inp.current_price) / inp.historical_baseline
    url_drag = (1.0 - inp.url_score / 100.0) * inp.urgency_factor
    di = price_inflation_factor - url_drag

    price_delta_pct = round(
        ((inp.current_price - inp.historical_baseline) / inp.historical_baseline) * 100, 2
    )

    if di > 1.25:
        decision = "OVERPRICED_HIGH_INFLATION"
        buy_window = "HOLD_OR_BUY_REFURBISHED"
        advice = (
            "Current prices are inflated by chipflation. "
            "Hold existing device or explore certified refurbished / previous-gen alternatives."
        )
    elif di >= 0.95:
        decision = "STABLE_MODERATE_PRICING"
        buy_window = "BUY_WITH_CASHBACK_EMI"
        advice = (
            "Pricing is moderate. Only proceed with a No-Cost EMI + bank cashback stack "
            "to offset chipflation surcharge."
        )
    else:
        decision = "OPTIMAL_BUY_WINDOW"
        buy_window = "BUY_NOW"
        advice = "Excellent pricing window. Purchase now to lock in below-baseline value."

    market_status = "INFLATED" if ci > 1.10 else "STABLE" if ci > 0.98 else "DEFLATING"

    return ChipflationResult(
        decision_index=round(di, 3),
        decision=decision,
        buy_window=buy_window,
        advice=advice,
        price_vs_baseline_pct=price_delta_pct,
        chipflation_index=round(ci, 3),
        driver=driver,
        market_status=market_status,
        seasonal_hint=SEASONAL_HINTS.get(cat, "Check major sale events in your region."),
    )
