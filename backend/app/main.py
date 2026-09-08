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
            "POST /api/v1/scrape",
            "POST /api/v1/price-compare",
            "GET  /api/v1/platforms",
            "GET  /api/v1/chipflation/trends",
            "GET  /api/v1/chipflation/refresh",
            "GET  /api/v1/predictions",
            "POST /api/v1/deals/submit",
            "POST /api/v1/deals/vote",
            "GET  /api/v1/deals",
            "GET  /api/v1/deals/stats",
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


# ─── Price Scraper & Comparison Endpoints ───────────────────────────────────

@app.post("/api/v1/scrape", tags=["Price Scraper"])
async def scrape_product_price(url: str):
    """
    Scrape real-time price from Amazon.in or Flipkart.com product URL.
    Returns product title, current price, availability, and metadata.
    """
    from app.engines.scraping_engine import scrape_product
    try:
        result = await scrape_product(url)
        return {
            "product_id": result.product_id,
            "platform": result.platform,
            "title": result.title,
            "price": result.price,
            "currency": result.currency,
            "image_url": result.image_url,
            "availability": result.availability,
            "rating": result.rating,
            "review_count": result.review_count,
            "url": result.url,
            "scraped_at": result.scraped_at,
            "error": result.error,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/price-compare", tags=["Price Comparison"])
async def compare_prices(query: str, category: str = "general"):
    """
    Compare prices across 10+ e-commerce platforms simultaneously.
    Returns lowest, highest, average prices and per-platform breakdown.
    """
    from app.engines.price_comparison import compare_prices as compare
    try:
        result = await compare(query, category)
        return {
            "product_query": result.product_query,
            "category": result.category,
            "lowest_price": result.lowest_price,
            "highest_price": result.highest_price,
            "avg_price": result.avg_price,
            "savings_vs_highest": result.savings_vs_highest,
            "best_deal_platform": result.best_deal_platform,
            "platforms_checked": result.platforms_checked,
            "comparison_time": result.comparison_time,
            "prices": [
                {
                    "platform": p.platform,
                    "price": p.price,
                    "url": p.url,
                    "availability": p.availability,
                    "seller": p.seller,
                    "shipping": p.shipping,
                    "total_cost": p.total_cost,
                    "error": p.error,
                }
                for p in result.prices
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/platforms", tags=["Price Comparison"])
def get_platforms():
    """List all supported e-commerce platforms for price comparison."""
    from app.engines.price_comparison import get_supported_platforms
    return {"platforms": get_supported_platforms()}


# ─── TrendForce / Chipflation Live Data ─────────────────────────────────────

@app.get("/api/v1/chipflation/trends", tags=["Chipflation Live"])
async def get_chipflation_trends():
    """
    Get live chipflation trends from TrendForce/DRAMeXchange.
    Returns component-level price changes and predictions.
    """
    from app.engines.trendforce import get_chipflation_trends as fetch_trends, calculate_composite_chipflation_index
    try:
        trends = await fetch_trends()
        composite_index = calculate_composite_chipflation_index(trends)
        
        return {
            "composite_index": composite_index,
            "market_status": "INFLATED" if composite_index > 1.10 else "STABLE" if composite_index > 0.98 else "DEFLATING",
            "components": [
                {
                    "component": t.component,
                    "current_price_usd": t.current_price,
                    "prev_price_usd": t.prev_price,
                    "change_pct": t.change_pct,
                    "trend": t.trend,
                    "prediction": t.prediction_next_quarter,
                    "confidence": t.confidence,
                    "sources": t.sources,
                }
                for t in trends
            ],
            "last_updated": trends[0].sources[0] if trends else "N/A",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chipflation/refresh", tags=["Chipflation Live"])
async def refresh_chipflation_data():
    """
    Force refresh of chipflation data from TrendForce.
    Useful for manual data refresh or admin operations.
    """
    from app.engines.trendforce import fetch_trendforce_latest
    try:
        data_points = await fetch_trendforce_latest()
        
        # Update DB with fresh data
        from app.db import update_chipflation_index
        updated = 0
        for dp in data_points:
            try:
                update_chipflation_index(
                    component_type=dp.component_type,
                    spot_price_usd=dp.spot_price_usd,
                    mom_growth_pct=dp.mom_growth_pct,
                    yoy_growth_pct=dp.yoy_growth_pct or 0.0,
                    source=dp.source
                )
                updated += 1
            except Exception:
                pass
        
        return {
            "status": "ok",
            "data_points_found": len(data_points),
            "database_updates": updated,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── ML Price Predictions ───────────────────────────────────────────────────

@app.get("/api/v1/predictions", tags=["ML Predictions"])
def get_price_predictions(category: str = None):
    """
    Get ML-based price predictions for components or a specific category.
    Uses linear regression on historical TrendForce data.
    """
    from app.engines.ml_predictor import predict_all_components, get_category_price_outlook
    try:
        if category:
            outlook = get_category_price_outlook(category)
            return {"category_outlook": outlook}
        else:
            predictions = predict_all_components()
            return {
                "predictions": [
                    {
                        "component": p.component,
                        "current_price": p.current_price,
                        "predicted_1m": p.predicted_price_1m,
                        "predicted_3m": p.predicted_price_3m,
                        "predicted_6m": p.predicted_price_6m,
                        "trend": p.trend,
                        "confidence": p.confidence,
                        "factors": p.factors,
                        "recommendation": p.recommendation,
                    }
                    for p in predictions
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Deal Verification & Community ──────────────────────────────────────────

@app.post("/api/v1/deals/submit", tags=["Deal Verification"])
def submit_deal(deal_data: dict):
    """
    Submit a deal for community verification.
    Other users can vote on whether the deal is real.
    """
    from app.engines.deal_verification import submit_deal as submit, DealSubmission
    try:
        deal = DealSubmission(
            product_url=deal_data.get("product_url", ""),
            platform=deal_data.get("platform", ""),
            product_title=deal_data.get("product_title", ""),
            deal_price=deal_data.get("deal_price", 0.0),
            original_price=deal_data.get("original_price", 0.0),
            coupon_code=deal_data.get("coupon_code"),
            submitted_by=deal_data.get("submitted_by", "anonymous"),
            notes=deal_data.get("notes"),
        )
        result = submit(deal)
        return {
            "deal_id": result.deal_id,
            "status": result.verification_status,
            "message": "Deal submitted for verification",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/deals/vote", tags=["Deal Verification"])
def vote_deal(deal_id: str, vote: str, voter_id: str, reason: str = None):
    """
    Vote on a deal (up = real deal, down = fake/expired).
    Helps community verify deal authenticity.
    """
    from app.engines.deal_verification import vote_on_deal, DealVote
    try:
        vote_obj = DealVote(
            deal_id=deal_id,
            voter_id=voter_id,
            vote=vote,
            reason=reason,
        )
        result = vote_on_deal(deal_id, vote_obj)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/deals", tags=["Deal Verification"])
def list_deals(platform: str = None, status: str = None, min_discount_pct: float = 0):
    """
    List community-submitted deals with optional filters.
    Returns deals sorted by vote score (best deals first).
    """
    from app.engines.deal_verification import list_deals as list_d
    try:
        deals = list_d(platform=platform, status=status, min_discount_pct=min_discount_pct)
        return {
            "deals": [
                {
                    "deal_id": d.deal_id,
                    "product_url": d.product_url,
                    "platform": d.platform,
                    "product_title": d.product_title,
                    "deal_price": d.deal_price,
                    "original_price": d.original_price,
                    "discount_pct": round((d.original_price - d.deal_price) / d.original_price * 100, 1) if d.original_price > 0 else 0,
                    "coupon_code": d.coupon_code,
                    "submitted_by": d.submitted_by,
                    "submitted_at": d.submitted_at,
                    "votes_up": d.votes_up,
                    "votes_down": d.votes_down,
                    "verification_status": d.verification_status,
                    "notes": d.notes,
                }
                for d in deals
            ],
            "total": len(deals),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/deals/stats", tags=["Deal Verification"])
def deal_stats():
    """Get overall deal verification statistics."""
    from app.engines.deal_verification import get_deal_stats
    return get_deal_stats()


# ─── Combined Master Endpoint ─────────────────────────────────────────────────

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
