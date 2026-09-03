"""
Pydantic request/response schemas for all API endpoints.
Keeping these separate from engine logic keeps main.py clean.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ─── Module 6: Device Longevity ───────────────────────────────────────────────

class URLRequest(BaseModel):
    category: str = Field(..., examples=["mobile"])
    age_months: int = Field(..., ge=0, examples=[42])
    battery_health_pct: float = Field(..., ge=0, le=100, examples=[72.0])
    storage_health_pct: float = Field(..., ge=0, le=100, examples=[85.0])
    physical_condition: float = Field(..., ge=0.0, le=1.0, examples=[0.85])
    eol_months: Optional[int] = Field(None, examples=[60])
    max_lifespan_years: Optional[float] = Field(None, examples=[5.0])


# ─── Module 2: Chipflation Decision Index ─────────────────────────────────────

class ChipflationRequest(BaseModel):
    category: str = Field(..., examples=["laptop"])
    current_price: float = Field(..., gt=0, examples=[75000])
    historical_baseline: float = Field(..., gt=0, examples=[62000])
    url_score: float = Field(default=70.0, ge=0, le=100, examples=[70.0])
    urgency_factor: float = Field(default=1.0, ge=0.5, le=2.0, examples=[1.0])
    chipflation_index: Optional[float] = Field(None, examples=[1.18])


# ─── Module 7: EMI Audit ──────────────────────────────────────────────────────

class EMIRequest(BaseModel):
    product_msrp: float = Field(..., gt=0, examples=[40000])
    no_cost_discount: float = Field(default=0.0, ge=0, examples=[2500])
    bank_processing_fee: float = Field(default=299.0, ge=0, examples=[299])
    tenure_months: int = Field(..., gt=0, examples=[6])
    forgone_cash_discount: float = Field(default=0.0, ge=0, examples=[1500])
    exchange_bonus: float = Field(default=0.0, ge=0, examples=[0])


class EMIScheduleRequest(BaseModel):
    product_msrp: float = Field(..., gt=0, examples=[40000])
    annual_rate_pct: float = Field(default=13.0, ge=0, le=100, examples=[13.0])
    tenure_months: int = Field(..., gt=0, examples=[6])
    no_cost_discount: float = Field(default=0.0, ge=0, examples=[2500])


# ─── Module 3 & 4: Recommendations ───────────────────────────────────────────

class RecommendRequest(BaseModel):
    category: str = Field(..., examples=["mobile"])
    use_case: str = Field(..., examples=["gaming"])
    max_budget_inr: float = Field(..., gt=0, examples=[35000])
    min_ram_gb: Optional[int] = Field(None, examples=[8])
    min_storage_gb: Optional[int] = Field(None, examples=[128])
    prefer_refurbished: bool = Field(default=False)


# ─── Combined Master Endpoint ─────────────────────────────────────────────────

class FullDecisionRequest(BaseModel):
    # Current device telemetry
    current_category: str = Field(..., examples=["mobile"])
    current_age_months: int = Field(..., ge=0, examples=[42])
    current_battery_health_pct: float = Field(..., ge=0, le=100, examples=[72.0])
    current_storage_health_pct: float = Field(..., ge=0, le=100, examples=[85.0])
    current_physical_condition: float = Field(..., ge=0.0, le=1.0, examples=[0.85])

    # Target purchase intent
    target_use_case: str = Field(..., examples=["gaming"])
    max_budget_inr: float = Field(..., gt=0, examples=[35000])
    target_current_price: float = Field(..., gt=0, examples=[32000])
    target_historical_baseline: float = Field(..., gt=0, examples=[27000])

    # Financing
    emi_tenure_months: int = Field(default=6, gt=0)
    bank_processing_fee: float = Field(default=299.0, ge=0)
    forgone_cash_discount: float = Field(default=1500.0, ge=0)
    no_cost_discount: float = Field(default=2000.0, ge=0)

    # Optional filters
    min_ram_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    prefer_refurbished: bool = False
