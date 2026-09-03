"""
AIDE-OS Backend — FastAPI Application Entry Point
All 7 engines wired into REST endpoints.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.engines.url_engine import URLInput, calculate_url
from app.engines.chipflation_engine import ChipflationInput, calculate_di
from app.engines.emi_engine import EMIInput, calculate_true_emi_cost
from app.engines.recommendation_engine import RecommendationInput, recommend_products

app = FastAPI(
    title="AIDE-OS API",
    description="AI-Driven Electronic Device Ecosystem — Open Source Decision Engine",
    version="4.0.0-PROD",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic request schemas ────────────────────────────────────────────────

class URLRequest(BaseModel):
    category: str = Field(..., example="mobile")
    age_months: int = Field(..., ge=0, example=42)
    battery_health_pct: float = Field(..., ge=0, le=100, example=72.0)
    storage_health_pct: float = Field(..., ge=0, le=100, example=85.0)
    physical_condition: float = Field(..., ge=0.0, le=1.0, example=0.85)
    eol_months: Optional[int] = Field(None, example=60)
    max_lifespan_years: Optional[float] = Field(None, example=5.0)


class ChipflationRequest(BaseModel):
    category: str = Field(..., example="laptop")
    current_price: float = Field(..., gt=0, example=75000)
    historical_baseline: float = Field(..., gt=0, example=62000)
    url_score: float = Field(default=70.0, ge=0, le=100, example=70.0)
    urgency_factor: float = Field(default=1.0, example=1.0)
    chipflation_index: Optional[float] = Field(None, example=1.18)


class EMIRequest(BaseModel):
    product_msrp: float = Field(..., gt=0, example=40000)
    no_cost_discount: float = Field(default=0.0, ge=0, example=2500)
    bank_processing_fee: float = Field(default=299.0, ge=0, example=299)
    tenure_months: int = Field(..., gt=0, example=6)
    forgone_cash_discount: float = Field(default=0.0, ge=0, example=1500)
    exchange_bonus: float = Field(default=0.0, ge=0, example=0)


class RecommendRequest(BaseModel):
    category: str = Field(..., example="mobile")
    use_case: str = Field(..., example="gaming")
    max_budget_inr: float = Field(..., gt=0, example=35000)
    min_ram_gb: Optional[int] = Field(None, example=8)
    min_storage_gb: Optional[int] = Field(None, example=128)
    prefer_refurbished: bool = Field(default=False)


class FullDecisionRequest(BaseModel):
    """
    Single-call endpoint: combines device diagnosis, chipflation check,
    product recommendation, and EMI audit in one shot.
    """
    # Current device
    current_category: str = Field(..., example="mobile")
    current_age_months: int = Field(..., ge=0, example=42)
    current_battery_health_pct: float = Field(..., ge=0, le=100, example=72.0)
    current_storage_health_pct: float = Field(..., ge=0, le=100, example=85.0)
    current_physical_condition: float = Field(..., ge=0.0, le=1.0, example=0.85)

    # Target purchase
    target_use_case: str = Field(..., example="gaming")
    max_budget_inr: float = Field(..., gt=0, example=35000)
    target_current_price: float = Field(..., gt=0, example=32000)
    target_historical_baseline: float = Field(..., gt=0, example=28000)

    # Financing
    emi_tenure_months: int = Field(default=6, gt=0)
    bank_processing_fee: float = Field(default=299.0, ge=0)
    forgone_cash_discount: float = Field(default=1500.0, ge=0)
    no_cost_discount: float = Field(default=2000.0, ge=0)

    # Optional
    min_ram_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    prefer_refurbished: bool = False


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "service": "AIDE-OS",
        "version": "4.0.0-PROD",
        "endpoints": [
            "/api/v1/device-longevity",
            "/api/v1/chipflation-index",
            "/api/v1/emi-audit",
            "/api/v1/recommend",
            "/api/v1/full-decision",
            "/api/v1/categories",
            "/api/v1/health",
        ],
        "docs": "/docs",
    }


@app.get("/api/v1/health", tags=["Info"])
def health():
    return {"status": "healthy", "service": "AIDE-OS", "version": "4.0.0-PROD",
            "timestamp": datetime.now().isoformat()}


@app.get("/api/v1/categories", tags=["Info"])
def list_categories():
    """Returns all supported device categories and their use-cases."""
    return {
        "categories": {
            "mobile":   ["gaming", "daily_tasks", "multitasking", "photography"],
            "laptop":   ["coding", "data_science", "video_editing", "productivity"],
            "audio":    ["anc", "music", "remote_work", "travel"],
            "video":    ["gaming", "streaming", "home_theater"],
            "memory":   ["fast_storage", "video_editing", "gaming"],
            "wearable": ["fitness", "health_tracking", "daily_use"],
        }
    }


@app.post("/api/v1/device-longevity", tags=["Module 6 — URL Engine"])
def device_longevity(req: URLRequest):
    """
    Calculates Useful Remaining Life (URL) score and remaining years.
    Returns HOLD / CONSIDER_REPLACEMENT / REPLACE_IMMEDIATELY verdict.
    """
    try:
        result = calculate_url(URLInput(
            category=req.category,
            age_months=req.age_months,
            battery_health_pct=req.battery_health_pct,
            storage_health_pct=req.storage_health_pct,
            physical_condition=req.physical_condition,
            eol_months=req.eol_months,
            max_lifespan_years=req.max_lifespan_years,
        ))
        return {
            "url_score_pct": result.url_score_pct,
            "estimated_years_left": result.estimated_years_left,
            "decision": result.decision,
            "maintenance_advice": result.maintenance_advice,
            "component_scores": result.component_scores,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/chipflation-index", tags=["Module 2 — Chipflation Engine"])
def chipflation_index(req: ChipflationRequest):
    """
    Calculates the Dynamic Buy-vs-Hold Decision Index (DI).
    Returns BUY_NOW / BUY_WITH_CASHBACK_EMI / HOLD_OR_BUY_REFURBISHED.
    """
    try:
        result = calculate_di(ChipflationInput(
            category=req.category,
            current_price=req.current_price,
            historical_baseline=req.historical_baseline,
            url_score=req.url_score,
            urgency_factor=req.urgency_factor,
            chipflation_index=req.chipflation_index,
        ))
        return {
            "decision_index": result.decision_index,
            "decision": result.decision,
            "buy_window": result.buy_window,
            "advice": result.advice,
            "price_vs_baseline_pct": result.price_vs_baseline_pct,
            "chipflation_index": result.chipflation_index,
            "driver": result.driver,
            "market_status": result.market_status,
            "seasonal_hint": result.seasonal_hint,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/emi-audit", tags=["Module 7 — EMI Engine"])
def emi_audit(req: EMIRequest):
    """
    Audits No-Cost EMI plans. Exposes processing fees, GST on interest,
    and forgone cash discounts to reveal the true effective outlay.
    """
    try:
        result = calculate_true_emi_cost(EMIInput(
            product_msrp=req.product_msrp,
            no_cost_discount=req.no_cost_discount,
            bank_processing_fee=req.bank_processing_fee,
            tenure_months=req.tenure_months,
            forgone_cash_discount=req.forgone_cash_discount,
            exchange_bonus=req.exchange_bonus,
        ))
        return {
            "advertised_price": result.advertised_price,
            "breakdown": result.breakdown,
            "total_hidden_charges": result.total_hidden_charges,
            "true_effective_outlay": result.true_effective_outlay,
            "hidden_charge_pct": result.hidden_charge_pct,
            "monthly_emi": result.monthly_emi,
            "recommendation": result.recommendation,
            "advice": result.advice,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/recommend", tags=["Module 3&4 — Recommendation Engine"])
def recommend(req: RecommendRequest):
    """
    Returns primary recommendations, alternatives, and refurbished options
    matched to the user's use-case, budget, and spec requirements.
    """
    try:
        results = recommend_products(RecommendationInput(
            category=req.category,
            use_case=req.use_case,
            max_budget_inr=req.max_budget_inr,
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            prefer_refurbished=req.prefer_refurbished,
        ))
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/full-decision", tags=["Combined Decision Engine"])
def full_decision(req: FullDecisionRequest):
    """
    The master endpoint. Runs all four engines (URL + Chipflation + Recommend + EMI)
    and returns a single consolidated decision object.
    """
    try:
        # 1. URL Assessment
        url_result = calculate_url(URLInput(
            category=req.current_category,
            age_months=req.current_age_months,
            battery_health_pct=req.current_battery_health_pct,
            storage_health_pct=req.current_storage_health_pct,
            physical_condition=req.current_physical_condition,
        ))

        # 2. Chipflation DI (informed by URL score)
        di_result = calculate_di(ChipflationInput(
            category=req.current_category,
            current_price=req.target_current_price,
            historical_baseline=req.target_historical_baseline,
            url_score=url_result.url_score_pct,
        ))

        # 3. Recommendations
        rec_result = recommend_products(RecommendationInput(
            category=req.current_category,
            use_case=req.target_use_case,
            max_budget_inr=req.max_budget_inr,
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            prefer_refurbished=req.prefer_refurbished,
        ))

        # 4. EMI Audit
        emi_result = calculate_true_emi_cost(EMIInput(
            product_msrp=req.target_current_price,
            no_cost_discount=req.no_cost_discount,
            bank_processing_fee=req.bank_processing_fee,
            tenure_months=req.emi_tenure_months,
            forgone_cash_discount=req.forgone_cash_discount,
        ))

        # Master verdict
        should_buy = (
            url_result.decision == "REPLACE_IMMEDIATELY"
            or (url_result.decision == "CONSIDER_REPLACEMENT"
                and di_result.decision != "OVERPRICED_HIGH_INFLATION")
        )

        if url_result.decision == "HOLD_CURRENT_DEVICE":
            master_verdict = "HOLD_CURRENT_DEVICE"
            master_advice = url_result.maintenance_advice
        elif di_result.decision == "OVERPRICED_HIGH_INFLATION":
            master_verdict = "BUY_REFURBISHED_OR_WAIT"
            master_advice = (
                f"{di_result.advice} "
                f"Current device can last ~{url_result.estimated_years_left} more years."
            )
        elif di_result.decision == "OPTIMAL_BUY_WINDOW":
            master_verdict = "BUY_NOW"
            master_advice = di_result.advice
        else:
            master_verdict = "BUY_WITH_BEST_OFFER"
            master_advice = di_result.advice

        return {
            "master_verdict": master_verdict,
            "master_advice": master_advice,
            "device_longevity": {
                "url_score_pct": url_result.url_score_pct,
                "estimated_years_left": url_result.estimated_years_left,
                "decision": url_result.decision,
                "maintenance_advice": url_result.maintenance_advice,
                "component_scores": url_result.component_scores,
            },
            "market_analysis": {
                "decision_index": di_result.decision_index,
                "decision": di_result.decision,
                "buy_window": di_result.buy_window,
                "price_vs_baseline_pct": di_result.price_vs_baseline_pct,
                "chipflation_index": di_result.chipflation_index,
                "driver": di_result.driver,
                "market_status": di_result.market_status,
                "seasonal_hint": di_result.seasonal_hint,
            },
            "recommendations": rec_result,
            "emi_audit": {
                "advertised_price": emi_result.advertised_price,
                "breakdown": emi_result.breakdown,
                "total_hidden_charges": emi_result.total_hidden_charges,
                "true_effective_outlay": emi_result.true_effective_outlay,
                "hidden_charge_pct": emi_result.hidden_charge_pct,
                "monthly_emi": emi_result.monthly_emi,
                "recommendation": emi_result.recommendation,
                "advice": emi_result.advice,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
