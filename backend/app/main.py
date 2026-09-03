"""
AIDE-OS — FastAPI Application Entry Point v4.0.0-PROD
Clean, schema-separated implementation with all 5 endpoints.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import get_settings
from app.schemas import (
    URLRequest, ChipflationRequest, EMIRequest,
    RecommendRequest, FullDecisionRequest
)
from app.engines.url_engine import URLInput, calculate_url
from app.engines.chipflation_engine import ChipflationInput, calculate_di
from app.engines.emi_engine import EMIInput, calculate_true_emi_cost
from app.engines.recommendation_engine import RecommendationInput, recommend_products
from app.db import log_user_device, log_emi_audit

cfg = get_settings()

app = FastAPI(
    title=cfg.APP_NAME,
    description=(
        "AI-Driven Electronic Device Ecosystem — "
        "Dynamic Pricing, Longevity & Purchase Decision Engine"
    ),
    version=cfg.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Info ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "service": cfg.APP_NAME,
        "version": cfg.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "endpoints": [
            "GET  /api/v1/health",
            "GET  /api/v1/categories",
            "POST /api/v1/device-longevity",
            "POST /api/v1/chipflation-index",
            "POST /api/v1/emi-audit",
            "POST /api/v1/recommend",
            "POST /api/v1/full-decision",
        ],
    }


@app.get("/api/v1/health", tags=["Info"])
def health():
    return {
        "status": "healthy",
        "service": cfg.APP_NAME,
        "version": cfg.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/v1/categories", tags=["Info"])
def categories():
    """All supported device categories and their valid use-case values."""
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


# ─── Module 6: Device Longevity ───────────────────────────────────────────────

@app.post("/api/v1/device-longevity", tags=["Module 6 — URL Engine"])
def device_longevity(req: URLRequest):
    """
    Computes the Useful Remaining Life (URL) score for existing hardware.
    Returns a HOLD / CONSIDER_REPLACEMENT / REPLACE_IMMEDIATELY verdict
    with weighted component breakdown and targeted maintenance advice.
    """
    try:
        r = calculate_url(URLInput(
            category=req.category,
            age_months=req.age_months,
            battery_health_pct=req.battery_health_pct,
            storage_health_pct=req.storage_health_pct,
            physical_condition=req.physical_condition,
            eol_months=req.eol_months,
            max_lifespan_years=req.max_lifespan_years,
        ))
        # Log device telemetry to DB
        log_user_device({
            "session_id": None,
            "category": req.category,
            "device_brand": None,
            "device_model": None,
            "age_months": req.age_months,
            "battery_health_pct": req.battery_health_pct,
            "storage_health_pct": req.storage_health_pct,
            "physical_condition": req.physical_condition,
            "eol_months": req.eol_months,
            "url_score_pct": r.url_score_pct,
            "estimated_years_left": r.estimated_years_left,
            "decision": r.decision,
        })
        return {
            "url_score_pct": r.url_score_pct,
            "estimated_years_left": r.estimated_years_left,
            "decision": r.decision,
            "maintenance_advice": r.maintenance_advice,
            "component_scores": r.component_scores,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# ─── Module 2: Chipflation Decision Index ─────────────────────────────────────

@app.post("/api/v1/chipflation-index", tags=["Module 2 — Chipflation Engine"])
def chipflation_index(req: ChipflationRequest):
    """
    Calculates the Dynamic Buy-vs-Hold Decision Index (DI) based on
    upstream DRAM/NAND component inflation vs. the historical retail baseline.
    Returns BUY_NOW / BUY_WITH_CASHBACK_EMI / HOLD_OR_BUY_REFURBISHED.
    """
    try:
        r = calculate_di(ChipflationInput(
            category=req.category,
            current_price=req.current_price,
            historical_baseline=req.historical_baseline,
            url_score=req.url_score,
            urgency_factor=req.urgency_factor,
            chipflation_index=req.chipflation_index,
        ))
        return {
            "decision_index": r.decision_index,
            "decision": r.decision,
            "buy_window": r.buy_window,
            "advice": r.advice,
            "price_vs_baseline_pct": r.price_vs_baseline_pct,
            "chipflation_index": r.chipflation_index,
            "driver": r.driver,
            "market_status": r.market_status,
            "seasonal_hint": r.seasonal_hint,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# ─── Module 7: EMI Audit ──────────────────────────────────────────────────────

@app.post("/api/v1/emi-audit", tags=["Module 7 — EMI Engine"])
def emi_audit(req: EMIRequest):
    """
    Audits "No-Cost EMI" plans and exposes:
    bank processing fees, 18% GST on the interest component,
    and the forgone upfront cash/UPI discount.
    Returns true effective outlay and a PAY_UPFRONT vs. EMI_ACCEPTABLE verdict.
    """
    try:
        r = calculate_true_emi_cost(EMIInput(
            product_msrp=req.product_msrp,
            no_cost_discount=req.no_cost_discount,
            bank_processing_fee=req.bank_processing_fee,
            tenure_months=req.tenure_months,
            forgone_cash_discount=req.forgone_cash_discount,
            exchange_bonus=req.exchange_bonus,
        ))
        return {
            "advertised_price": r.advertised_price,
            "breakdown": r.breakdown,
            "total_hidden_charges": r.total_hidden_charges,
            "true_effective_outlay": r.true_effective_outlay,
            "hidden_charge_pct": r.hidden_charge_pct,
            "monthly_emi": r.monthly_emi,
            "recommendation": r.recommendation,
            "advice": r.advice,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# ─── Module 3 & 4: Recommendations ───────────────────────────────────────────

@app.post("/api/v1/recommend", tags=["Module 3 & 4 — Recommender"])
def recommend(req: RecommendRequest):
    """
    Maps user workload, budget, and spec requirements to matched products.
    Returns primary picks, alternatives, and certified refurbished options
    sorted by use-case match score with chipflation risk ratings.
    """
    try:
        return recommend_products(RecommendationInput(
            category=req.category,
            use_case=req.use_case,
            max_budget_inr=req.max_budget_inr,
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            prefer_refurbished=req.prefer_refurbished,
        ))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# ─── Combined Master Endpoint ─────────────────────────────────────────────────

@app.post("/api/v1/full-decision", tags=["Master — Full Decision Engine"])
def full_decision(req: FullDecisionRequest):
    """
    Single-call master endpoint. Runs all four engines in one lifecycle:
    URL Assessment → Chipflation DI → Product Recommendations → EMI Audit.
    Returns a consolidated master verdict with per-engine details.
    """
    try:
        url_r = calculate_url(URLInput(
            category=req.current_category,
            age_months=req.current_age_months,
            battery_health_pct=req.current_battery_health_pct,
            storage_health_pct=req.current_storage_health_pct,
            physical_condition=req.current_physical_condition,
        ))

        di_r = calculate_di(ChipflationInput(
            category=req.current_category,
            current_price=req.target_current_price,
            historical_baseline=req.target_historical_baseline,
            url_score=url_r.url_score_pct,
        ))

        rec_r = recommend_products(RecommendationInput(
            category=req.current_category,
            use_case=req.target_use_case,
            max_budget_inr=req.max_budget_inr,
            min_ram_gb=req.min_ram_gb,
            min_storage_gb=req.min_storage_gb,
            prefer_refurbished=req.prefer_refurbished,
        ))

        emi_r = calculate_true_emi_cost(EMIInput(
            product_msrp=req.target_current_price,
            no_cost_discount=req.no_cost_discount,
            bank_processing_fee=req.bank_processing_fee,
            tenure_months=req.emi_tenure_months,
            forgone_cash_discount=req.forgone_cash_discount,
        ))

        # Master verdict logic
        if url_r.decision == "HOLD_CURRENT_DEVICE":
            verdict = "HOLD_CURRENT_DEVICE"
            advice  = url_r.maintenance_advice
        elif di_r.decision == "OVERPRICED_HIGH_INFLATION":
            verdict = "BUY_REFURBISHED_OR_WAIT"
            advice  = f"{di_r.advice} Your device has ~{url_r.estimated_years_left} yrs left."
        elif di_r.decision == "OPTIMAL_BUY_WINDOW":
            verdict = "BUY_NOW"
            advice  = di_r.advice
        else:
            verdict = "BUY_WITH_BEST_OFFER"
            advice  = di_r.advice

        # Log to DB
        log_user_device({
            "session_id": None,
            "category": req.current_category,
            "device_brand": None,
            "device_model": None,
            "age_months": req.current_age_months,
            "battery_health_pct": req.current_battery_health_pct,
            "storage_health_pct": req.current_storage_health_pct,
            "physical_condition": req.current_physical_condition,
            "eol_months": None,
            "url_score_pct": url_r.url_score_pct,
            "estimated_years_left": url_r.estimated_years_left,
            "decision": url_r.decision,
        })
        log_emi_audit({
            "gadget_id": None,
            "session_id": None,
            "product_msrp": req.target_current_price,
            "no_cost_discount": req.no_cost_discount,
            "bank_processing_fee": req.bank_processing_fee,
            "tenure_months": req.emi_tenure_months,
            "forgone_cash_discount": req.forgone_cash_discount,
            "exchange_bonus": 0.0,
            "total_hidden_charges": emi_r.total_hidden_charges,
            "true_effective_outlay": emi_r.true_effective_outlay,
            "recommendation": emi_r.recommendation,
        })

        return {
            "master_verdict": verdict,
            "master_advice": advice,
            "device_longevity": {
                "url_score_pct": url_r.url_score_pct,
                "estimated_years_left": url_r.estimated_years_left,
                "decision": url_r.decision,
                "maintenance_advice": url_r.maintenance_advice,
                "component_scores": url_r.component_scores,
            },
            "market_analysis": {
                "decision_index": di_r.decision_index,
                "decision": di_r.decision,
                "buy_window": di_r.buy_window,
                "price_vs_baseline_pct": di_r.price_vs_baseline_pct,
                "chipflation_index": di_r.chipflation_index,
                "driver": di_r.driver,
                "market_status": di_r.market_status,
                "seasonal_hint": di_r.seasonal_hint,
            },
            "recommendations": rec_r,
            "emi_audit": {
                "advertised_price": emi_r.advertised_price,
                "breakdown": emi_r.breakdown,
                "total_hidden_charges": emi_r.total_hidden_charges,
                "true_effective_outlay": emi_r.true_effective_outlay,
                "hidden_charge_pct": emi_r.hidden_charge_pct,
                "monthly_emi": emi_r.monthly_emi,
                "recommendation": emi_r.recommendation,
                "advice": emi_r.advice,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
