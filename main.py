from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime
import math

app = FastAPI(
    title="AIDE-OS Production Decision Engine",
    version="4.0.0-PROD",
    description="AI-Driven Electronic Device Ecosystem - Open Source"
)

# Add CORS middleware for web frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserRequirementInput(BaseModel):
    category: str = Field(..., description="Device category: Mobile, Laptop, Audio, Video, Memory, Wearable")
    target_workload: str = Field(..., description="Use case: Gaming, Coding, Daily_Tasks, Professional, Creative")
    max_budget: float = Field(..., gt=0, description="Maximum budget in local currency")

class DeviceTelemetryInput(BaseModel):
    category: str = Field(..., description="Device category")
    age_months: int = Field(..., ge=0, description="Device age in months")
    battery_health_pct: float = Field(..., ge=0, le=100, description="Battery health percentage")
    storage_health_pct: float = Field(..., ge=0, le=100, description="Storage health percentage") 
    eol_months: int = Field(..., gt=0, description="End of life in months")
    physical_condition: float = Field(..., ge=0, le=1, description="Physical condition score 0-1")
    max_hardware_lifespan_years: float = Field(..., gt=0, description="Maximum expected lifespan")

class EMITrackerInput(BaseModel):
    product_msrp: float = Field(..., gt=0, description="Manufacturer's suggested retail price")
    no_cost_discount: float = Field(default=0.0, ge=0, description="Subsidized interest by seller")
    bank_processing_fee: float = Field(default=299.0, ge=0, description="Bank processing fee")
    tenure_months: int = Field(..., gt=0, description="EMI tenure in months")
    forgone_cash_discount: float = Field(default=0.0, ge=0, description="Lost upfront discount")

class ChipflationInput(BaseModel):
    category: str = Field(..., description="Product category")
    current_price: float = Field(..., gt=0, description="Current market price")
    historical_baseline: float = Field(..., gt=0, description="Historical baseline price")
    chipflation_index: float = Field(default=1.0, ge=0, description="Component inflation factor")

# Core Calculation Engines
@app.post("/api/v1/evaluate-device-longevity")
def evaluate_device_longevity(telemetry: DeviceTelemetryInput):
    """
    Calculates Useful Remaining Life (URL) and estimated years left for current hardware.
    Uses weighted scoring: Battery (35%), Storage (25%), Age (25%), Physical (15%)
    """
    try:
        # Normalize health factors (0-1 scale)
        bh = max(0.0, min(1.0, telemetry.battery_health_pct / 100.0))
        sh = max(0.0, min(1.0, telemetry.storage_health_pct / 100.0))
        age_factor = max(0.0, 1.0 - (telemetry.age_months / float(telemetry.eol_months)))
        phys = max(0.0, min(1.0, telemetry.physical_condition))
        
        # Weighted URL Score calculation
        url_score = (0.35 * bh + 0.25 * sh + 0.25 * age_factor + 0.15 * phys) * 100.0
        years_left = round((url_score / 100.0) * telemetry.max_hardware_lifespan_years, 1)
        
        # Decision logic
        decision = "REPLACE_HARDWARE"
        maintenance_advice = "Hardware has reached end of life. Upgrade recommended."
        
        if url_score >= 60.0:
            decision = "HOLD_CURRENT_DEVICE"
            if bh < 0.75:
                maintenance_advice = f"Replace battery ($20-$30). Device will run for another {years_left} years."
            elif sh < 0.70:
                maintenance_advice = f"Storage showing wear. Consider cleanup or replacement. {years_left} years remaining."
            else:
                maintenance_advice = f"Device condition is solid. Expected to remain usable for {years_left} more years."
        elif url_score >= 40.0:
            decision = "CONSIDER_REPLACEMENT"
            maintenance_advice = f"Device is aging but functional. Plan replacement within 6-12 months. {years_left} years estimated."
            
        return {
            "url_score_pct": round(url_score, 2),
            "estimated_years_left": years_left,
            "decision": decision,
            "maintenance_step": maintenance_advice,
            "component_scores": {
                "battery_normalized": round(bh * 100, 1),
                "storage_normalized": round(sh * 100, 1),
                "age_factor": round(age_factor * 100, 1),
                "physical_condition": round(phys * 100, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

@app.post("/api/v1/track-emi-hidden-charges")
def track_emi_hidden_charges(emi: EMITrackerInput):
    """
    Audit 'No-Cost EMI' plans to extract processing fees, GST on interest, and lost cash discounts.
    Reveals the true cost beyond advertised pricing.
    """
    try:
        # 1. GST on processing fee (18% in India)
        processing_fee_gst = emi.bank_processing_fee * 0.18
        
        # 2. 18% GST on the subsidized interest component (not absorbed by seller/bank)
        interest_gst_charge = emi.no_cost_discount * 0.18
        
        # 3. Total Hidden Surcharges
        total_hidden_charges = (
            emi.bank_processing_fee + 
            processing_fee_gst + 
            interest_gst_charge + 
            emi.forgone_cash_discount
        )
        
        true_effective_cost = emi.product_msrp + total_hidden_charges
        hidden_charge_percentage = (total_hidden_charges / emi.product_msrp) * 100
        
        # Generate recommendation
        if total_hidden_charges > 1000:
            recommendation = "PAY_UPFRONT_CASH"
            advice = "Hidden charges exceed ₹1000. Pay upfront to save money."
        elif hidden_charge_percentage > 5:
            recommendation = "RECONSIDER_EMI"
            advice = f"Hidden charges are {hidden_charge_percentage:.1f}% of product price. Consider alternatives."
        else:
            recommendation = "NO_COST_EMI_ACCEPTABLE"
            advice = "Hidden charges are minimal. EMI option is reasonable."
        
        return {
            "advertised_price": emi.product_msrp,
            "hidden_charges_breakdown": {
                "bank_processing_fee": emi.bank_processing_fee,
                "gst_on_processing_fee_18pct": round(processing_fee_gst, 2),
                "unrefundable_gst_on_interest_18pct": round(interest_gst_charge, 2),
                "forgone_upfront_cash_discount": emi.forgone_cash_discount
            },
            "total_hidden_surcharges": round(total_hidden_charges, 2),
            "true_effective_outlay": round(true_effective_cost, 2),
            "hidden_charge_percentage": round(hidden_charge_percentage, 2),
            "recommendation": recommendation,
            "advice": advice
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"EMI calculation error: {str(e)}")

@app.post("/api/v1/chipflation-decision-index")
def calculate_chipflation_decision_index(chipflation: ChipflationInput):
    """
    Calculates Dynamic Buy-vs-Hold Decision Index based on chipflation and market conditions.
    DI > 1.25: OVERPRICED, DI 0.95-1.25: MODERATE, DI < 0.95: OPTIMAL BUY
    """
    try:
        # Calculate Decision Index (DI)
        price_inflation_factor = (chipflation.chipflation_index * chipflation.current_price) / chipflation.historical_baseline
        
        # Urgency factor (could be enhanced with user input)
        urgency_factor = 1.0  # Default neutral urgency
        
        decision_index = price_inflation_factor - (1 - urgency_factor)
        
        # Decision logic
        if decision_index > 1.25:
            decision = "OVERPRICED_HOLD"
            advice = "Market prices inflated due to chipflation. Consider waiting or refurbished alternatives."
            buy_window = "WAIT_FOR_CORRECTION"
        elif 0.95 <= decision_index <= 1.25:
            decision = "MODERATE_PRICING"
            advice = "Reasonable pricing. Buy only with cashback/EMI benefits to offset costs."
            buy_window = "CONDITIONAL_BUY"
        else:
            decision = "OPTIMAL_BUY_WINDOW" 
            advice = "Excellent pricing despite market conditions. Recommended immediate purchase."
            buy_window = "BUY_NOW"
            
        price_vs_baseline_pct = ((chipflation.current_price - chipflation.historical_baseline) / chipflation.historical_baseline) * 100
        
        return {
            "decision_index": round(decision_index, 3),
            "decision": decision,
            "buy_window": buy_window,
            "advice": advice,
            "price_vs_baseline_pct": round(price_vs_baseline_pct, 2),
            "chipflation_impact": {
                "component_inflation_factor": chipflation.chipflation_index,
                "price_inflation_factor": round(price_inflation_factor, 3),
                "market_assessment": "INFLATED" if chipflation.chipflation_index > 1.1 else "STABLE"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Chipflation calculation error: {str(e)}")

@app.get("/api/v1/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "AIDE-OS Decision Engine",
        "version": "4.0.0-PROD",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
def root():
    """Root endpoint with system information"""
    return {
        "service": "AIDE-OS - AI-Driven Electronic Device Ecosystem",
        "description": "Open-source system for intelligent gadget purchasing decisions",
        "version": "4.0.0-PROD",
        "features": [
            "Device longevity assessment",
            "Hidden EMI charge detection", 
            "Chipflation impact analysis",
            "Buy vs Hold recommendations"
        ],
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)