"""
AIDE-OS ML Price Prediction Engine
Forecast future price movements using historical chipflation data.
Uses statistical methods (linear regression, moving averages) - no external ML libs needed.
"""
import math
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger("aide-os.ml_predictor")


@dataclass
class PriceDataPoint:
    date: str
    price: float
    component: str
    source: str = "historical"


@dataclass
class PricePrediction:
    component: str
    current_price: float
    predicted_price_1m: float
    predicted_price_3m: float
    predicted_price_6m: float
    trend: str  # rising, falling, stable
    confidence: float  # 0-1
    factors: list = field(default_factory=list)
    recommendation: str = ""


# Historical price data (simulated from TrendForce/DRAMeXchange patterns)
HISTORICAL_PRICES = {
    'DDR5_SODIMM': [
        ('2024-01', 3.20), ('2024-04', 3.45), ('2024-07', 3.80),
        ('2024-10', 3.95), ('2025-01', 4.05), ('2025-04', 4.12),
    ],
    'LPDDR5X': [
        ('2024-01', 2.90), ('2024-04', 3.15), ('2024-07', 3.45),
        ('2024-10', 3.60), ('2025-01', 3.75), ('2025-04', 3.85),
    ],
    'NAND_3D_TLC': [
        ('2024-01', 0.045), ('2024-04', 0.052), ('2024-07', 0.058),
        ('2024-10', 0.061), ('2025-01', 0.063), ('2025-04', 0.065),
    ],
    'HBM3E': [
        ('2024-01', 12.50), ('2024-04', 14.20), ('2024-07', 16.00),
        ('2024-10', 17.20), ('2025-01', 17.90), ('2025-04', 18.40),
    ],
    'LPDDR4X': [
        ('2024-01', 1.85), ('2024-04', 1.95), ('2024-07', 2.05),
        ('2024-10', 2.10), ('2025-01', 2.15), ('2025-04', 2.20),
    ],
}


def _linear_regression(prices: list[float]) -> tuple[float, float]:
    """Simple linear regression: returns (slope, intercept)."""
    n = len(prices)
    if n < 2:
        return 0.0, prices[0] if prices else 0.0
    
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(prices) / n
    
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, prices))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    
    if denominator == 0:
        return 0.0, y_mean
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    return slope, intercept


def _moving_average(prices: list[float], window: int = 3) -> float:
    """Calculate moving average."""
    if len(prices) < window:
        return sum(prices) / len(prices) if prices else 0.0
    return sum(prices[-window:]) / window


def _calculate_r_squared(prices: list[float], slope: float, intercept: float) -> float:
    """Calculate R-squared for regression confidence."""
    n = len(prices)
    if n < 3:
        return 0.5
    
    y_mean = sum(prices) / n
    ss_total = sum((y - y_mean) ** 2 for y in prices)
    
    if ss_total == 0:
        return 1.0
    
    ss_residual = 0
    for i, y in enumerate(prices):
        y_pred = slope * i + intercept
        ss_residual += (y - y_pred) ** 2
    
    r_squared = 1 - (ss_residual / ss_total)
    return max(0.0, min(1.0, r_squared))


def predict_price(component: str) -> PricePrediction:
    """Predict future price for a component based on historical data."""
    history = HISTORICAL_PRICES.get(component, [])
    
    if not history:
        return PricePrediction(
            component=component,
            current_price=0.0,
            predicted_price_1m=0.0,
            predicted_price_3m=0.0,
            predicted_price_6m=0.0,
            trend="unknown",
            confidence=0.0,
            factors=["No historical data available"],
            recommendation="Insufficient data for prediction"
        )
    
    prices = [p[1] for p in history]
    current_price = prices[-1]
    
    # Linear regression
    slope, intercept = _linear_regression(prices)
    r_squared = _calculate_r_squared(prices, slope, intercept)
    
    # Moving average
    ma = _moving_average(prices)
    
    # Predict future prices (each step = ~3 months based on data)
    n = len(prices)
    pred_1m = slope * (n + 0.33) + intercept  # 1 month ahead
    pred_3m = slope * (n + 1) + intercept      # 3 months ahead
    pred_6m = slope * (n + 2) + intercept      # 6 months ahead
    
    # Ensure predictions are positive
    pred_1m = max(0.01, pred_1m)
    pred_3m = max(0.01, pred_3m)
    pred_6m = max(0.01, pred_6m)
    
    # Determine trend
    if slope > 0.05:
        trend = "rising"
    elif slope < -0.05:
        trend = "falling"
    else:
        trend = "stable"
    
    # Confidence based on R-squared and data points
    confidence = r_squared * min(1.0, n / 6)  # More data = higher confidence
    
    # Generate factors and recommendations
    factors = []
    if slope > 0:
        factors.append(f"Prices rising at ~{slope:.3f} per quarter")
        factors.append("AI server demand driving component shortages")
    elif slope < 0:
        factors.append(f"Prices declining at ~{abs(slope):.3f} per quarter")
        factors.append("Supply normalization underway")
    else:
        factors.append("Prices stable near historical average")
    
    if confidence > 0.7:
        factors.append(f"High confidence model (R²={r_squared:.2f})")
    
    # Recommendation
    change_3m_pct = ((pred_3m - current_price) / current_price) * 100
    
    if trend == "rising" and change_3m_pct > 5:
        recommendation = "BUY_NOW: Prices expected to rise further"
    elif trend == "falling" and change_3m_pct < -5:
        recommendation = "HOLD: Wait for prices to drop further"
    elif abs(change_3m_pct) < 3:
        recommendation = "FLEXIBLE: Prices stable, buy when convenient"
    else:
        recommendation = "MONITOR: Check again in 2-4 weeks"
    
    return PricePrediction(
        component=component,
        current_price=current_price,
        predicted_price_1m=round(pred_1m, 4),
        predicted_price_3m=round(pred_3m, 4),
        predicted_price_6m=round(pred_6m, 4),
        trend=trend,
        confidence=round(confidence, 2),
        factors=factors,
        recommendation=recommendation
    )


def predict_all_components() -> list[PricePrediction]:
    """Predict prices for all tracked components."""
    predictions = []
    for component in HISTORICAL_PRICES.keys():
        predictions.append(predict_price(component))
    return predictions


def get_category_price_outlook(category: str) -> dict:
    """Get price outlook for a device category based on its key components."""
    category_components = {
        'mobile': ['LPDDR5X', 'NAND_3D_TLC'],
        'laptop': ['DDR5_SODIMM', 'NAND_3D_TLC'],
        'audio': ['LPDDR4X'],  # Less impacted
        'video': ['NAND_3D_TLC'],
        'memory': ['NAND_3D_TLC'],
        'wearable': ['LPDDR4X', 'NAND_3D_TLC'],
    }
    
    components = category_components.get(category, ['DDR5_SODIMM'])
    predictions = [predict_price(c) for c in components]
    
    # Average outlook
    avg_confidence = sum(p.confidence for p in predictions) / len(predictions)
    avg_change_3m = sum(
        ((p.predicted_price_3m - p.current_price) / p.current_price * 100) 
        for p in predictions
    ) / len(predictions)
    
    if avg_change_3m > 5:
        overall_trend = "rising"
        advice = "Prices expected to increase; consider buying soon"
    elif avg_change_3m < -5:
        overall_trend = "falling"
        advice = "Prices dropping; can afford to wait"
    else:
        overall_trend = "stable"
        advice = "Prices stable; buy when ready"
    
    return {
        "category": category,
        "components": [p.component for p in predictions],
        "overall_trend": overall_trend,
        "avg_price_change_3m_pct": round(avg_change_3m, 2),
        "confidence": round(avg_confidence, 2),
        "advice": advice,
        "predictions": [
            {
                "component": p.component,
                "current": p.current_price,
                "predicted_3m": p.predicted_price_3m,
                "trend": p.trend,
                "recommendation": p.recommendation
            }
            for p in predictions
        ]
    }
