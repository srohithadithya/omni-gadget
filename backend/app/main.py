"""
AIDE-OS — FastAPI Application Entry Point v4.0.0-PROD
Clean, schema-separated implementation with all 5 endpoints.
Telegram bot runs as a daemon thread inside the same process.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger("aide-os")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Telegram bot daemon thread on server startup."""
    from app.bot_runner import start_bot_if_configured
    bot_thread = start_bot_if_configured()
    if bot_thread:
        logger.info("Telegram bot running in background (thread=%s)", bot_thread.name)
    yield
    logger.info("Shutting down AIDE-OS …")
from app.schemas import (
    URLRequest, ChipflationRequest, EMIRequest, EMIScheduleRequest,
    RecommendRequest, FullDecisionRequest
)
from app.engines.url_engine import URLInput, calculate_url
from app.engines.chipflation_engine import ChipflationInput, calculate_di
from app.engines.emi_engine import EMIInput, calculate_true_emi_cost
from app.engines.emi_schedule import generate_emi_schedule
from app.engines.recommendation_engine import RecommendationInput, recommend_products
from app.db import log_user_device, log_emi_audit, update_chipflation_index, get_latest_chipflation_all
from app.middleware import SessionMiddleware
from app.analytics import AnalyticsService

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
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=getattr(cfg, "SECRET_KEY", "aide-os-default-secret"),
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
            "POST /api/v1/emi-schedule",
            "POST /api/v1/recommend",
            "POST /api/v1/full-decision",
            "GET  /api/v1/history",
            "GET  /api/v1/popular",
            "GET  /api/v1/trends",
        ],
    }


@app.get("/health", tags=["Info"])
def health_root():
    """Simple health check for Render/production load balancers."""
    return {"status": "ok"}


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
def device_longevity(req: URLRequest, request: Request = None):
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
        session_id = getattr(request.state, "session_id", None) if request else None
        # Log device telemetry to DB
        log_user_device({
            "session_id": session_id,
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


@app.post("/api/v1/emi-schedule", tags=["Module 7 — EMI Engine"])
def emi_schedule(req: EMIScheduleRequest):
    """
    Generate a month-by-month amortization schedule for an EMI plan.
    For No-Cost EMI (annual_rate_pct=0), interest is zero but GST on the
    seller-subsidised interest is noted as a buyer obligation.
    """
    try:
        principal = req.product_msrp - req.no_cost_discount
        if principal < 0:
            raise ValueError("no_cost_discount cannot exceed product_msrp")

        schedule = generate_emi_schedule(
            principal=principal,
            annual_rate_pct=req.annual_rate_pct,
            tenure_months=req.tenure_months,
        )

        total_interest = round(sum(row["interest_component"] for row in schedule), 2)
        total_gst_on_interest = round(total_interest * cfg.GST_RATE, 2)
        total_cost = round(principal + total_interest + total_gst_on_interest, 2)

        is_no_cost = req.annual_rate_pct == 0 or req.no_cost_discount > 0

        return {
            "schedule": schedule,
            "totals": {
                "total_principal": round(principal, 2),
                "total_interest": total_interest,
                "total_gst_on_interest": total_gst_on_interest,
                "total_cost": total_cost,
            },
            "is_no_cost_emi": is_no_cost,
            "no_cost_note": (
                "This is a No-Cost EMI plan. The interest is absorbed by the seller, "
                "but the buyer is still charged 18% GST on the interest component."
                if is_no_cost else None
            ),
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


# ─── Admin: Chipflation Index Management ─────────────────────────────────────

@app.get("/api/v1/admin/chipflation/latest", tags=["Admin"])
def chipflation_latest():
    """Get latest chipflation_index rows per component for dashboard."""
    try:
        rows = get_latest_chipflation_all()
        return {
            "components": [
                {
                    "component_type": r["component_type"],
                    "spot_price_usd": float(r["spot_price_usd"]),
                    "mom_growth_pct": float(r["mom_growth_pct"]),
                    "yoy_growth_pct": float(r["yoy_growth_pct"]),
                    "source": r["source"],
                    "recorded_at": r["recorded_at"].isoformat() if r["recorded_at"] else None,
                }
                for r in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/admin/chipflation/update", tags=["Admin"])
def chipflation_update(component_type: str, spot_price_usd: float,
                       mom_growth_pct: float, yoy_growth_pct: float,
                       source: str = "admin"):
    """Insert a new chipflation data point. Requires component_type (LPDDR5X, DDR5_SODIMM, etc.)."""
    try:
        update_chipflation_index(component_type, spot_price_usd, mom_growth_pct, yoy_growth_pct, source)
        return {"status": "ok", "component": component_type, "message": "Chipflation index updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Combined Master Endpoint ─────────────────────────────────────────────────

# ─── Analytics Endpoints ─────────────────────────────────────────────────────

@app.get("/api/v1/history", tags=["Analytics"])
def get_session_history(request: Request):
    """
    Return the last 10 decisions for the current anonymous session.
    Session ID is read from the signed cookie.
    """
    try:
        session_id = getattr(request.state, "session_id", None)
        if not session_id:
            return {"history": [], "session_id": None}
        history = AnalyticsService.get_user_history(session_id)
        return {"history": history, "session_id": session_id}
    except Exception:
        return {"history": [], "session_id": None}


@app.get("/api/v1/popular", tags=["Analytics"])
def get_popular():
    """
    Return the top 5 most recommended product categories (aggregated across sessions).
    """
    try:
        popular = AnalyticsService.get_popular_products()
        return {"popular_products": popular}
    except Exception:
        return {"popular_products": []}


@app.get("/api/v1/trends", tags=["Analytics"])
def get_trends():
    """
    Return average URL scores over time (daily, last 30 days).
    """
    try:
        trends = AnalyticsService.get_market_trends()
        return {"trends": trends}
    except Exception:
        return {"trends": []}


@app.post("/api/v1/full-decision", tags=["Master — Full Decision Engine"])
def full_decision(req: FullDecisionRequest, request: Request = None):
    """
    Single-call master endpoint. Runs all four engines in one lifecycle:
    URL Assessment → Chipflation DI → Product Recommendations → EMI Audit.
    Returns a consolidated master verdict with per-engine details.
    """
    try:
        session_id = getattr(request.state, "session_id", None) if request else None
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
            "session_id": session_id,
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
            "session_id": session_id,
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
