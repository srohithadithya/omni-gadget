"""
Module 3 & 4: Product Recommendation Engine
Matches user requirements to products and surfaces alternatives/refurbished options.
"""
from dataclasses import dataclass, field
from typing import List, Optional


# Static product catalogue — in production this is DB-driven + live scraped
PRODUCT_CATALOGUE = {
    "mobile": [
        {
            "id": "mob_001", "brand": "Samsung", "model": "Galaxy S25",
            "tier": "flagship", "price_inr": 80000, "baseline_inr": 75000,
            "ram_gb": 12, "storage_gb": 256, "display": "120Hz AMOLED",
            "use_cases": ["gaming", "multitasking", "photography"],
            "chipflation_risk": "medium",
            "pros": ["Best-in-class camera", "7 years OS updates", "Compact form factor"],
            "cons": ["Premium pricing due to LPDDR5X", "No charger in box"],
            "rating": 4.5, "reviews": 12400,
            "refurbished_available": True, "refurb_price_inr": 55000,
            "refurb_source": "Amazon Renewed / Samsung Certified",
        },
        {
            "id": "mob_002", "brand": "Nothing", "model": "Phone 4(a)",
            "tier": "mid-range", "price_inr": 30000, "baseline_inr": 27000,
            "ram_gb": 12, "storage_gb": 256, "display": "120Hz AMOLED",
            "use_cases": ["daily_tasks", "social_media", "gaming"],
            "chipflation_risk": "low",
            "pros": ["Unique design", "Clean Android", "Great price-to-performance"],
            "cons": ["Limited accessories ecosystem", "No IP rating"],
            "rating": 4.3, "reviews": 5800,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "mob_003", "brand": "Samsung", "model": "Galaxy S23",
            "tier": "previous-gen", "price_inr": 52000, "baseline_inr": 70000,
            "ram_gb": 8, "storage_gb": 256, "display": "120Hz AMOLED",
            "use_cases": ["gaming", "multitasking", "daily_tasks"],
            "chipflation_risk": "low",
            "pros": ["Proven reliability", "Below-baseline pricing", "Excellent camera"],
            "cons": ["Older chipset", "Shorter remaining OS support window"],
            "rating": 4.4, "reviews": 28000,
            "refurbished_available": True, "refurb_price_inr": 38000,
            "refurb_source": "Amazon Renewed",
        },
        {
            "id": "mob_004", "brand": "Redmi", "model": "Note 15 Pro",
            "tier": "mid-range", "price_inr": 22000, "baseline_inr": 20000,
            "ram_gb": 8, "storage_gb": 128, "display": "120Hz AMOLED",
            "use_cases": ["daily_tasks", "social_media"],
            "chipflation_risk": "low",
            "pros": ["Best value at price point", "Large battery", "Fast charging"],
            "cons": ["MIUI ads", "Average camera in low light"],
            "rating": 4.1, "reviews": 41000,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "mob_005", "brand": "OnePlus", "model": "11R",
            "tier": "upper-mid", "price_inr": 40000, "baseline_inr": 42000,
            "ram_gb": 16, "storage_gb": 256, "display": "120Hz AMOLED",
            "use_cases": ["gaming", "multitasking"],
            "chipflation_risk": "low",
            "pros": ["Below baseline — good deal", "Fast charging 100W", "OxygenOS"],
            "cons": ["No wireless charging", "Plastic back"],
            "rating": 4.3, "reviews": 9200,
            "refurbished_available": True, "refurb_price_inr": 28000,
            "refurb_source": "Cashify / Amazon Renewed",
        },
    ],
    "laptop": [
        {
            "id": "lap_001", "brand": "Lenovo", "model": "IdeaPad Slim 5",
            "tier": "mainstream", "price_inr": 68000, "baseline_inr": 60000,
            "ram_gb": 16, "storage_gb": 512, "display": "14\" FHD IPS",
            "use_cases": ["coding", "data_science", "productivity"],
            "chipflation_risk": "high",
            "pros": ["16GB DDR5", "Good keyboard", "Decent build quality"],
            "cons": ["Mediocre battery life", "Fans audible under load"],
            "rating": 4.2, "reviews": 7600,
            "refurbished_available": True, "refurb_price_inr": 48000,
            "refurb_source": "Lenovo Certified Refurbished",
        },
        {
            "id": "lap_002", "brand": "ASUS", "model": "ExpertBook P1",
            "tier": "business", "price_inr": 72000, "baseline_inr": 65000,
            "ram_gb": 16, "storage_gb": 512, "display": "15.6\" FHD",
            "use_cases": ["coding", "productivity", "data_science"],
            "chipflation_risk": "high",
            "pros": ["Military-grade durability", "Long battery", "Business-class warranty"],
            "cons": ["Heavier than ultrabooks", "Integrated GPU only"],
            "rating": 4.4, "reviews": 3200,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "lap_003", "brand": "Lenovo", "model": "ThinkPad E14 (Open-Box)",
            "tier": "certified-open-box", "price_inr": 54000, "baseline_inr": 70000,
            "ram_gb": 16, "storage_gb": 512, "display": "14\" FHD IPS",
            "use_cases": ["coding", "data_science", "video_editing"],
            "chipflation_risk": "low",
            "pros": ["Below baseline price", "DDR5 RAM", "Excellent keyboard", "ThinkPad reliability"],
            "cons": ["Open-box unit — verify condition on arrival"],
            "rating": 4.5, "reviews": 15800,
            "refurbished_available": True, "refurb_price_inr": 54000,
            "refurb_source": "Amazon Renewed / Flipkart SmartBuy",
        },
        {
            "id": "lap_004", "brand": "Apple", "model": "MacBook Air M4",
            "tier": "premium", "price_inr": 110000, "baseline_inr": 105000,
            "ram_gb": 16, "storage_gb": 512, "display": "13.6\" Liquid Retina",
            "use_cases": ["video_editing", "creative", "coding"],
            "chipflation_risk": "low",
            "pros": ["Best-in-class performance per watt", "18hr battery", "Fanless"],
            "cons": ["Premium price", "Limited port selection"],
            "rating": 4.8, "reviews": 22000,
            "refurbished_available": True, "refurb_price_inr": 85000,
            "refurb_source": "Apple Certified Refurbished",
        },
    ],
    "audio": [
        {
            "id": "aud_001", "brand": "Sony", "model": "WH-1000XM5",
            "tier": "premium", "price_inr": 26000, "baseline_inr": 30000,
            "use_cases": ["anc", "remote_work", "travel"],
            "chipflation_risk": "low",
            "pros": ["Industry-leading ANC", "LDAC support", "30hr battery"],
            "cons": ["Non-foldable design", "Sensitive to wind noise"],
            "rating": 4.7, "reviews": 45000,
            "refurbished_available": True, "refurb_price_inr": 18000,
            "refurb_source": "Amazon Renewed",
        },
        {
            "id": "aud_002", "brand": "OnePlus", "model": "Buds Pro 3",
            "tier": "mid-range", "price_inr": 11000, "baseline_inr": 10500,
            "use_cases": ["anc", "daily_tasks", "music"],
            "chipflation_risk": "low",
            "pros": ["Good ANC", "LHDC codec", "Spatial audio"],
            "cons": ["Average mic quality", "App required for full features"],
            "rating": 4.2, "reviews": 8700,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "aud_003", "brand": "Anker", "model": "Soundcore Space Q45",
            "tier": "budget-anc", "price_inr": 7000, "baseline_inr": 7000,
            "use_cases": ["anc", "budget", "daily_tasks"],
            "chipflation_risk": "very_low",
            "pros": ["Best ANC under ₹7k", "50hr battery", "LDAC"],
            "cons": ["Plasticky build", "Average soundstage"],
            "rating": 4.1, "reviews": 19000,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
    ],
    "video": [
        {
            "id": "vid_001", "brand": "LG", "model": "55\" B4 OLED",
            "tier": "premium", "price_inr": 120000, "baseline_inr": 115000,
            "use_cases": ["gaming", "streaming", "home_theater"],
            "chipflation_risk": "low",
            "pros": ["Perfect blacks", "120Hz HDMI 2.1", "webOS smart platform"],
            "cons": ["Risk of burn-in", "Premium pricing"],
            "rating": 4.7, "reviews": 11200,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "vid_002", "brand": "TCL", "model": "55\" C655 QLED",
            "tier": "mid-range", "price_inr": 55000, "baseline_inr": 52000,
            "use_cases": ["streaming", "daily_use", "gaming"],
            "chipflation_risk": "low",
            "pros": ["Bright QLED panel", "Google TV", "Dolby Vision"],
            "cons": ["Mediocre local dimming", "Average motion handling"],
            "rating": 4.2, "reviews": 6500,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "vid_003", "brand": "Hisense", "model": "55\" U7K Mini-LED",
            "tier": "value-premium", "price_inr": 65000, "baseline_inr": 68000,
            "use_cases": ["streaming", "gaming", "home_theater"],
            "chipflation_risk": "very_low",
            "pros": ["Mini-LED backlight", "Below baseline", "144Hz gaming"],
            "cons": ["Less brand recognition", "Limited service network in India"],
            "rating": 4.3, "reviews": 3200,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
    ],
    "memory": [
        {
            "id": "mem_001", "brand": "Crucial", "model": "T500 1TB NVMe Gen4",
            "tier": "mainstream", "price_inr": 8500, "baseline_inr": 7000,
            "use_cases": ["video_editing", "gaming", "fast_storage"],
            "chipflation_risk": "high",
            "pros": ["Gen4 speeds", "DRAM cache", "Reliable brand"],
            "cons": ["Inflated above baseline due to NAND prices"],
            "rating": 4.5, "reviews": 21000,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "mem_002", "brand": "Lexar", "model": "NM790 1TB NVMe",
            "tier": "budget", "price_inr": 5800, "baseline_inr": 5500,
            "use_cases": ["daily_use", "gaming", "budget_storage"],
            "chipflation_risk": "medium",
            "pros": ["Good price per GB", "Respectable Gen4 speeds"],
            "cons": ["DRAM-less (HMB only)", "Lesser brand warranty support"],
            "rating": 4.2, "reviews": 9400,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "mem_003", "brand": "Samsung", "model": "990 EVO 1TB",
            "tier": "mainstream", "price_inr": 9000, "baseline_inr": 7500,
            "use_cases": ["video_editing", "gaming"],
            "chipflation_risk": "high",
            "pros": ["Samsung reliability", "PCIe 4x2 hybrid interface"],
            "cons": ["Priced above baseline", "Not the fastest Gen4 option"],
            "rating": 4.4, "reviews": 14000,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
    ],
    "wearable": [
        {
            "id": "wear_001", "brand": "Samsung", "model": "Galaxy Watch 7",
            "tier": "mainstream", "price_inr": 28000, "baseline_inr": 27000,
            "use_cases": ["health_tracking", "fitness", "notifications"],
            "chipflation_risk": "low",
            "pros": ["ECG + BIA sensors", "Android ecosystem", "Wear OS 5"],
            "cons": ["1.5-day battery", "Best with Samsung phones"],
            "rating": 4.3, "reviews": 7800,
            "refurbished_available": True, "refurb_price_inr": 19000,
            "refurb_source": "Amazon Renewed",
        },
        {
            "id": "wear_002", "brand": "Fitbit", "model": "Charge 6",
            "tier": "fitness-band", "price_inr": 14000, "baseline_inr": 13000,
            "use_cases": ["fitness", "health_tracking"],
            "chipflation_risk": "very_low",
            "pros": ["7-day battery", "Google integration", "Excellent health sensors"],
            "cons": ["Limited app ecosystem", "Requires Fitbit Premium for full features"],
            "rating": 4.2, "reviews": 5600,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
        {
            "id": "wear_003", "brand": "Amazfit", "model": "Balance",
            "tier": "budget-smart", "price_inr": 12000, "baseline_inr": 12000,
            "use_cases": ["fitness", "daily_use", "budget"],
            "chipflation_risk": "very_low",
            "pros": ["14-day battery", "Built-in Alexa", "Great display"],
            "cons": ["Zepp OS has limited third-party apps"],
            "rating": 4.1, "reviews": 4200,
            "refurbished_available": False, "refurb_price_inr": None,
            "refurb_source": None,
        },
    ],
}


USE_CASE_MAP = {
    "gaming": ["gaming", "multitasking"],
    "coding": ["coding", "data_science", "productivity"],
    "data_science": ["coding", "data_science"],
    "video_editing": ["video_editing", "creative"],
    "daily_tasks": ["daily_tasks", "social_media"],
    "music": ["music", "anc"],
    "anc": ["anc", "remote_work", "travel"],
    "streaming": ["streaming", "home_theater"],
    "health_tracking": ["health_tracking", "fitness"],
    "fitness": ["fitness", "health_tracking"],
    "productivity": ["productivity", "coding"],
    "remote_work": ["remote_work", "anc"],
    "travel": ["travel", "anc"],
    "fast_storage": ["fast_storage", "video_editing"],
}


@dataclass
class RecommendationInput:
    category: str
    use_case: str
    max_budget_inr: float
    min_ram_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    prefer_refurbished: bool = False


@dataclass
class ProductMatch:
    product: dict
    match_score: float
    value_verdict: str          # GREAT_VALUE / FAIR / OVERPRICED
    is_primary: bool


def _get_catalogue(cat: str) -> list:
    """Try DB first, fall back to static PRODUCT_CATALOGUE."""
    try:
        from app.db import query_products
        rows = query_products(cat, [], inp.max_budget_inr if hasattr(inp, 'max_budget_inr') else 999999)
        if rows:
            return [_pg_row_to_product(r) for r in rows]
    except Exception:
        pass
    return PRODUCT_CATALOGUE.get(cat, [])


def _pg_row_to_product(row) -> dict:
    """Convert a psycopg2 RealDictRow to the dict format the scoring engine expects."""
    return {
        'id': str(row.get('gadget_id', '')),
        'brand': row.get('brand', ''),
        'model_name': row.get('model_name', ''),
        'tier': row.get('tier', ''),
        'price_inr': float(row.get('current_price', 0)),
        'baseline_inr': float(row.get('historical_baseline', 0)),
        'ram_gb': row.get('ram_gb'),
        'storage_gb': row.get('storage_gb'),
        'display': row.get('display_spec', ''),
        'display_spec': row.get('display_spec', ''),
        'use_cases': row.get('use_cases', []),
        'chipflation_risk': row.get('chipflation_risk', 'medium'),
        'pros': row.get('pros', []),
        'cons': row.get('cons', []),
        'rating': float(row.get('rating', 4.0)),
        'reviews': row.get('review_count', 0),
        'review_count': row.get('review_count', 0),
        'refurbished_available': row.get('refurb_available', False),
        'refurb_price_inr': float(row['refurb_price']) if row.get('refurb_price') else None,
        'refurb_source': row.get('refurb_source'),
    }


def recommend_products(inp: RecommendationInput) -> dict:
    cat = inp.category.lower()
    catalogue = _get_catalogue(cat)

    if not catalogue:
        return {"primary": [], "alternatives": [], "refurbished": []}

    # Resolve use case aliases
    target_uses = USE_CASE_MAP.get(inp.use_case.lower(), [inp.use_case.lower()])

    scored = []
    for p in catalogue:
        score = 0.0

        # Use-case match
        p_uses = [u.lower() for u in p.get("use_cases", [])]
        use_overlap = len(set(target_uses) & set(p_uses))
        score += use_overlap * 30

        # Budget fit
        price = p["price_inr"]
        if inp.prefer_refurbished and p.get("refurb_price_inr"):
            price = p["refurb_price_inr"]

        if price <= inp.max_budget_inr:
            # More budget headroom = slightly better deal
            budget_ratio = (inp.max_budget_inr - price) / inp.max_budget_inr
            score += 20 + budget_ratio * 10
        else:
            score -= 40  # over budget penalty

        # RAM filter
        if inp.min_ram_gb and p.get("ram_gb"):
            if p["ram_gb"] >= inp.min_ram_gb:
                score += 15
            else:
                score -= 20

        # Storage filter
        if inp.min_storage_gb and p.get("storage_gb"):
            if p["storage_gb"] >= inp.min_storage_gb:
                score += 10
            else:
                score -= 15

        # Rating bonus
        score += p.get("rating", 3.0) * 5

        # Chipflation penalty
        risk_penalty = {"high": -15, "medium": -5, "low": 0, "very_low": 5}
        score += risk_penalty.get(p.get("chipflation_risk", "low"), 0)

        # Value verdict
        baseline = p["baseline_inr"]
        if price <= baseline * 0.95:
            value_verdict = "GREAT_VALUE"
        elif price <= baseline * 1.10:
            value_verdict = "FAIR"
        else:
            value_verdict = "OVERPRICED"

        scored.append((score, p, value_verdict))

    # Normalize keys: ensure model_name exists (static catalogue uses 'model')
    for score, p, vv in scored:
        if 'model' in p and 'model_name' not in p:
            p['model_name'] = p['model']

    scored.sort(key=lambda x: x[0], reverse=True)

    primary = []
    alternatives = []
    refurbished = []

    for rank, (score, p, vv) in enumerate(scored):
        match = ProductMatch(product=p, match_score=round(score, 1),
                             value_verdict=vv, is_primary=(rank == 0))
        if p.get("tier") in ("certified-open-box",) or (
            inp.prefer_refurbished and p.get("refurb_price_inr")
        ):
            refurbished.append(match.__dict__)
        elif rank == 0:
            primary.append(match.__dict__)
        elif rank <= 2:
            alternatives.append(match.__dict__)

        # Also collect refurbished listings from primary/alt products
        if p.get("refurb_price_inr") and not inp.prefer_refurbished:
            refurbished.append({
                "product": {**p, "display_price": p["refurb_price_inr"],
                             "source": p["refurb_source"]},
                "match_score": round(score * 0.9, 1),
                "value_verdict": "GREAT_VALUE",
                "is_primary": False,
            })

    return {
        "primary": primary[:2],
        "alternatives": alternatives[:3],
        "refurbished": refurbished[:3],
    }
