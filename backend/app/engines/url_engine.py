"""
Module 6: Useful Remaining Life (URL) Engine
Calculates device longevity based on telemetry inputs.
"""
from dataclasses import dataclass
from typing import Optional


WEIGHTS = {"battery": 0.35, "storage": 0.25, "age": 0.25, "physical": 0.15}

CATEGORY_LIFESPAN = {
    "mobile": 5.0,
    "laptop": 6.0,
    "audio": 5.0,
    "video": 8.0,
    "memory": 7.0,
    "wearable": 4.0,
}

CATEGORY_EOL_MONTHS = {
    "mobile": 60,
    "laptop": 72,
    "audio": 60,
    "video": 96,
    "memory": 84,
    "wearable": 48,
}


@dataclass
class URLInput:
    category: str
    age_months: int
    battery_health_pct: float          # 0–100
    storage_health_pct: float          # 0–100
    physical_condition: float          # 0.0–1.0
    eol_months: Optional[int] = None
    max_lifespan_years: Optional[float] = None


@dataclass
class URLResult:
    url_score_pct: float
    estimated_years_left: float
    decision: str                      # HOLD / CONSIDER_REPLACEMENT / REPLACE
    maintenance_advice: str
    component_scores: dict


def calculate_url(inp: URLInput) -> URLResult:
    cat = inp.category.lower()
    eol = inp.eol_months or CATEGORY_EOL_MONTHS.get(cat, 60)
    lifespan = inp.max_lifespan_years or CATEGORY_LIFESPAN.get(cat, 5.0)

    bh = max(0.0, min(1.0, inp.battery_health_pct / 100.0))
    sh = max(0.0, min(1.0, inp.storage_health_pct / 100.0))
    age_factor = max(0.0, 1.0 - (inp.age_months / float(eol)))
    phys = max(0.0, min(1.0, inp.physical_condition))

    url_score = (
        WEIGHTS["battery"] * bh
        + WEIGHTS["storage"] * sh
        + WEIGHTS["age"] * age_factor
        + WEIGHTS["physical"] * phys
    ) * 100.0

    years_left = round((url_score / 100.0) * lifespan, 1)

    # Decision
    if url_score >= 60.0:
        decision = "HOLD_CURRENT_DEVICE"
        if bh < 0.75:
            advice = (
                f"Battery at {inp.battery_health_pct:.0f}% — replace it (₹800–₹2,000) "
                f"to extend useful life by ~{years_left} more years."
            )
        elif sh < 0.70:
            advice = (
                f"Storage showing wear. Clear temp files or replace storage. "
                f"Device still good for ~{years_left} years."
            )
        else:
            advice = f"Device is in good shape. Expect ~{years_left} more years of usable life."
    elif url_score >= 40.0:
        decision = "CONSIDER_REPLACEMENT"
        advice = (
            f"Device is aging. Plan a replacement in 6–12 months. "
            f"Estimated ~{years_left} years remaining."
        )
    else:
        decision = "REPLACE_IMMEDIATELY"
        advice = "Device has reached end of practical life. Upgrade recommended now."

    return URLResult(
        url_score_pct=round(url_score, 2),
        estimated_years_left=years_left,
        decision=decision,
        maintenance_advice=advice,
        component_scores={
            "battery_pct": round(bh * 100, 1),
            "storage_pct": round(sh * 100, 1),
            "age_factor_pct": round(age_factor * 100, 1),
            "physical_pct": round(phys * 100, 1),
        },
    )
