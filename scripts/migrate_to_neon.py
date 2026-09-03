#!/usr/bin/env python3
"""
AIDE-OS — Neon PostgreSQL Migration Script
============================================
Creates all tables and seeds initial data for production deployment.

Usage:
    # Set DATABASE_URL env var first, then:
    python scripts/migrate_to_neon.py

    # Or pass inline:
    DATABASE_URL="postgresql://..." python scripts/migrate_to_neon.py
"""

import os
import sys
import uuid
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor


# ─── Schema DDL ───────────────────────────────────────────────────────────────

SCHEMA_SQL = """
-- Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Gadgets Master Catalogue ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gadgets (
    gadget_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category        VARCHAR(20) NOT NULL CHECK (category IN ('mobile','laptop','audio','video','memory','wearable')),
    brand           VARCHAR(60) NOT NULL,
    model_name      VARCHAR(120) NOT NULL,
    tier            VARCHAR(40),
    base_msrp       NUMERIC(12, 2) NOT NULL,
    current_price   NUMERIC(12, 2) NOT NULL,
    historical_baseline NUMERIC(12, 2) NOT NULL,
    ram_gb          SMALLINT,
    storage_gb      INT,
    display_spec    VARCHAR(120),
    chipflation_risk VARCHAR(20) DEFAULT 'medium',
    use_cases       TEXT[],
    pros            TEXT[],
    cons            TEXT[],
    rating          NUMERIC(3,1),
    review_count    INT DEFAULT 0,
    refurb_available BOOLEAN DEFAULT FALSE,
    refurb_price    NUMERIC(12, 2),
    refurb_source   VARCHAR(120),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gadgets_category ON gadgets(category);
CREATE INDEX IF NOT EXISTS idx_gadgets_price    ON gadgets(current_price);

-- ─── Chipflation Spot Price Log ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chipflation_index (
    index_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_type  VARCHAR(50) NOT NULL,
    spot_price_usd  NUMERIC(10, 4) NOT NULL,
    mom_growth_pct  NUMERIC(6, 2) NOT NULL,
    yoy_growth_pct  NUMERIC(6, 2),
    source          VARCHAR(80),
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chipflation_component ON chipflation_index(component_type);
CREATE INDEX IF NOT EXISTS idx_chipflation_time      ON chipflation_index(recorded_at DESC);

-- ─── User Devices (telemetry submissions) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS user_devices (
    device_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          VARCHAR(64),
    category            VARCHAR(20) NOT NULL,
    device_brand        VARCHAR(60),
    device_model        VARCHAR(120),
    age_months          SMALLINT NOT NULL,
    battery_health_pct  NUMERIC(5, 2) NOT NULL,
    storage_health_pct  NUMERIC(5, 2) NOT NULL,
    physical_condition  NUMERIC(3, 2) NOT NULL,
    eol_months          SMALLINT,
    url_score_pct       NUMERIC(5, 2),
    estimated_years_left NUMERIC(4, 1),
    decision            VARCHAR(40),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─── EMI Audit Log ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS emi_audit_log (
    audit_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gadget_id               UUID REFERENCES gadgets(gadget_id) ON DELETE SET NULL,
    session_id              VARCHAR(64),
    product_msrp            NUMERIC(12, 2) NOT NULL,
    no_cost_discount        NUMERIC(10, 2) DEFAULT 0,
    bank_processing_fee     NUMERIC(8, 2)  DEFAULT 299,
    tenure_months           SMALLINT NOT NULL,
    forgone_cash_discount   NUMERIC(10, 2) DEFAULT 0,
    exchange_bonus          NUMERIC(10, 2) DEFAULT 0,
    total_hidden_charges    NUMERIC(10, 2),
    true_effective_outlay   NUMERIC(12, 2),
    recommendation          VARCHAR(40),
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Price History Tracker ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS price_history (
    history_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gadget_id   UUID NOT NULL REFERENCES gadgets(gadget_id) ON DELETE CASCADE,
    price       NUMERIC(12, 2) NOT NULL,
    source      VARCHAR(80),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_price_history_gadget ON price_history(gadget_id, recorded_at DESC);

-- ─── Sale Event Calendar ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sale_events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name      VARCHAR(120) NOT NULL,
    platform        VARCHAR(60),
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    typical_discount_pct NUMERIC(4, 1),
    categories      TEXT[],
    notes           TEXT
);
"""


# ─── Seed Data ────────────────────────────────────────────────────────────────

CHIPFLATION_SEED = [
    ("LPDDR5X",     3.85,  4.20, 18.50, "TrendForce"),
    ("DDR5_SODIMM", 4.12,  3.80, 22.10, "TrendForce"),
    ("NAND_3D_TLC",  0.065, 5.10, 24.30, "DRAMeXchange"),
    ("HBM3E",       18.40,  2.10, 41.00, "TrendForce"),
    ("LPDDR4X",      2.20,  1.50,  8.20, "TrendForce"),
]

SALE_EVENTS_SEED = [
    ("Big Billion Days",       "Flipkart",  "2026-10-01", "2026-10-06", 20.0,
     ["mobile", "laptop", "audio", "video", "wearable"],
     "Biggest sale of the year"),
    ("Great Indian Festival",  "Amazon",    "2026-10-01", "2026-10-06", 18.0,
     ["mobile", "laptop", "audio", "video", "memory"],
     "Runs concurrent with Big Billion"),
    ("Republic Day Sale",      "All",       "2026-01-20", "2026-01-26", 12.0,
     ["mobile", "laptop", "audio"],
     "Good for smartphones"),
    ("Independence Day Sale",  "All",       "2026-08-10", "2026-08-15", 10.0,
     ["mobile", "laptop"],
     "Back-to-college overlap"),
    ("Prime Day",              "Amazon",    "2026-07-16", "2026-07-17", 15.0,
     ["audio", "memory", "wearable"],
     "Flash deals on accessories"),
    ("New Year Sale",          "All",       "2026-01-01", "2026-01-05", 10.0,
     ["video", "wearable"],
     "TV and smartwatch deals"),
    ("Black Friday",           "All",       "2026-11-27", "2026-11-30", 22.0,
     ["laptop", "mobile", "audio", "video", "memory"],
     "Best laptop deals"),
    ("Back to College",        "All",       "2026-07-01", "2026-08-31", 12.0,
     ["laptop", "mobile"],
     "Student discount stacking period"),
]

# 100 products — 18 from schema.sql + 82 additional realistic Indian-market gadgets
GADGETS_SEED = [
    # ── Mobile (20) ──────────────────────────────────────────────────────
    ("mobile", "Samsung", "Galaxy S25", "flagship", 79999, 80000, 75000,
     12, 256, "120Hz Dynamic AMOLED 2X", "medium",
     ["gaming", "multitasking", "photography"],
     ["Best-in-class camera", "7 years OS updates", "Compact form"],
     ["Premium pricing", "No charger in box"],
     4.5, 12400, True, 55000, "Amazon Renewed / Samsung Certified"),
    ("mobile", "Nothing", "Phone 4(a)", "mid-range", 29999, 30000, 27000,
     12, 256, "120Hz AMOLED", "low",
     ["daily_tasks", "social_media", "gaming"],
     ["Unique design", "Clean Android", "Great value"],
     ["Limited accessories", "No IP rating"],
     4.3, 5800, False, None, None),
    ("mobile", "Samsung", "Galaxy S23", "previous-gen", 69999, 52000, 70000,
     8, 256, "120Hz AMOLED", "low",
     ["gaming", "multitasking", "daily_tasks"],
     ["Proven reliability", "Below-baseline pricing", "Excellent camera"],
     ["Older chipset", "Shorter OS support window"],
     4.4, 28000, True, 38000, "Amazon Renewed"),
    ("mobile", "OnePlus", "11R", "upper-mid", 41999, 40000, 42000,
     16, 256, "120Hz AMOLED", "low",
     ["gaming", "multitasking"],
     ["Below baseline deal", "100W fast charging", "OxygenOS"],
     ["No wireless charging", "Plastic back"],
     4.3, 9200, True, 28000, "Cashify / Amazon Renewed"),
    ("mobile", "Apple", "iPhone 15", "flagship", 79900, 74000, 79900,
     6, 128, "6.1\" OLED", "low",
     ["photography", "daily_tasks", "multitasking"],
     ["iOS ecosystem", "A16 Bionic", "Dynamic Island"],
     ["60Hz display", "No charger in box"],
     4.5, 34000, True, 52000, "Amazon Renewed"),
    ("mobile", "Xiaomi", "14", "flagship", 69999, 62000, 69999,
     12, 256, "120Hz AMOLED", "medium",
     ["photography", "gaming", "multitasking"],
     ["Leica cameras", "Snapdragon 8 Gen 3", "Fast charging"],
     ["MIUI ads", "Inconsistent updates"],
     4.4, 8900, False, None, None),
    ("mobile", "Google", "Pixel 8a", "mid-range", 39999, 37000, 39999,
     8, 128, "120Hz OLED", "low",
     ["photography", "daily_tasks", "AI_features"],
     ["Pure Android", "Tensor G3 AI", "7 years updates"],
     ["Mediocre battery", "Average charging speed"],
     4.3, 6200, False, None, None),
    ("mobile", "Samsung", "Galaxy A55", "mid-range", 39999, 38000, 39999,
     8, 128, "120Hz AMOLED", "low",
     ["daily_tasks", "gaming", "photography"],
     ["IP67 rating", "Metal build", "Long updates"],
     ["Mediocre low-light camera", "Bloatware"],
     4.2, 11000, False, None, None),
    ("mobile", "Realme", "GT 6T", "upper-mid", 29999, 28000, 29999,
     8, 256, "120Hz AMOLED", "medium",
     ["gaming", "daily_tasks", "fast_charging"],
     ["120W charging", "Snapdragon 7+ Gen 2", "Bright display"],
     ["No IP rating", "Heavy MIUI skin"],
     4.2, 7500, False, None, None),
    ("mobile", "iQOO", "12", "flagship", 52999, 48000, 52999,
     12, 256, "120Hz AMOLED", "medium",
     ["gaming", "multitasking", "fast_charging"],
     ["Snapdragon 8 Gen 3", "120W flash charge", "Gaming triggers"],
     ["Average camera", "No wireless charging"],
     4.3, 5600, False, None, None),
    ("mobile", "Samsung", "Galaxy S24 Ultra", "flagship", 134999, 125000, 134999,
     12, 256, "120Hz Dynamic AMOLED 2X", "low",
     ["photography", "multitasking", "productivity"],
     ["S Pen", "Titanium build", "AI Galaxy features"],
     ["Very expensive", "Heavy"],
     4.7, 18000, True, 85000, "Samsung Certified"),
    ("mobile", "Apple", "iPhone SE 4", "mid-range", 49900, 49900, 49900,
     6, 128, "6.1\" OLED", "low",
     ["daily_tasks", "photography", "budget_apple"],
     ["Apple A18 chip", "OLED display", "Face ID"],
     ["Single camera", "Average battery"],
     4.3, 4500, False, None, None),
    ("mobile", "OnePlus", "Nord 4", "mid-range", 27999, 27000, 27999,
     8, 256, "120Hz AMOLED", "low",
     ["daily_tasks", "gaming", "multitasking"],
     ["Snapdragon 7+ Gen 3", "5500mAh battery", "Fast charging"],
     ["No IP rating", "Average camera"],
     4.2, 6800, False, None, None),
    ("mobile", "Samsung", "Galaxy M34", "budget", 18999, 17500, 18999,
     6, 128, "120Hz AMOLED", "very_low",
     ["daily_tasks", "battery_life", "budget"],
     ["6000mAh battery", "sAMOLED display", "Good value"],
     ["Mediocre camera", "Plastic build"],
     4.1, 15000, False, None, None),
    ("mobile", "Vivo", "T3 Pro", "upper-mid", 24999, 24000, 24999,
     8, 128, "120Hz AMOLED", "medium",
     ["gaming", "daily_tasks", "photography"],
     ["Dimensity 9200+", "Good cameras", "Slim design"],
     ["Funtouch OS bloat", "No stereo speakers"],
     4.1, 4200, False, None, None),
    ("mobile", "Motorola", "Edge 50 Pro", "upper-mid", 31999, 30000, 31999,
     8, 256, "120Hz pOLED", "low",
     ["photography", "daily_tasks", "multitasking"],
     ["Near-stock Android", "125W charging", "IP68"],
     ["Average gaming performance", "No wireless charging"],
     4.2, 3800, False, None, None),
    ("mobile", "Honor", "200 Pro", "upper-mid", 39999, 38000, 39999,
     12, 256, "120Hz OLED", "medium",
     ["photography", "daily_tasks", "multitasking"],
     ["Portrait camera", "Snapdragon 8s Gen 3", "Fast charging"],
     ["MagicOS bloat", "Mediocre ultra-wide"],
     4.2, 3200, False, None, None),
    ("mobile", "Samsung", "Galaxy Z Flip 5", "premium-fold", 99999, 85000, 99999,
     8, 256, "6.7\" Foldable AMOLED", "low",
     ["fashion", "daily_tasks", "compact"],
     ["Compact folded size", "Cover screen", "Flex mode"],
     ["Crease visible", "Battery life", "Fragile"],
     4.0, 7600, True, 62000, "Samsung Certified"),
    ("mobile", "Poco", "X6 Pro", "budget", 19999, 18500, 19999,
     8, 256, "120Hz AMOLED", "medium",
     ["gaming", "daily_tasks", "budget"],
     ["Dimensity 8300", "1.5K display", "Great value"],
     ["MIUI ads", "Average camera"],
     4.2, 9800, False, None, None),
    ("mobile", "Apple", "iPhone 16 Pro", "flagship", 134900, 134900, 134900,
     8, 256, "6.3\" ProMotion OLED", "low",
     ["photography", "video_recording", "productivity"],
     ["A18 Pro chip", "Camera Control button", "Titanium"],
     ["Very expensive", "No charger"],
     4.7, 12000, False, None, None),

    # ── Laptop (18) ──────────────────────────────────────────────────────
    ("laptop", "Lenovo", "IdeaPad Slim 5", "mainstream", 67999, 68000, 60000,
     16, 512, "14\" FHD IPS", "high",
     ["coding", "data_science", "productivity"],
     ["16GB DDR5", "Good keyboard", "Decent build"],
     ["Mediocre battery", "Audible fans under load"],
     4.2, 7600, True, 48000, "Lenovo Certified Refurbished"),
    ("laptop", "ASUS", "ExpertBook P1", "business", 71999, 72000, 65000,
     16, 512, "15.6\" FHD", "high",
     ["coding", "productivity", "data_science"],
     ["Military-grade durability", "Long battery", "Business warranty"],
     ["Heavier than ultrabooks", "Integrated GPU only"],
     4.4, 3200, False, None, None),
    ("laptop", "Apple", "MacBook Air M4", "premium", 109999, 110000, 105000,
     16, 512, "13.6\" Liquid Retina", "low",
     ["video_editing", "creative", "coding"],
     ["Best performance per watt", "18hr battery", "Fanless"],
     ["Premium price", "Limited ports"],
     4.8, 22000, True, 85000, "Apple Certified Refurbished"),
    ("laptop", "HP", "Pavilion Plus 14", "mainstream", 64999, 62000, 64999,
     16, 512, "14\" 2.8K OLED", "high",
     ["coding", "creative", "productivity"],
     ["OLED display", "Good build", "Fast charging"],
     ["Average battery", "Fan noise under load"],
     4.2, 5400, False, None, None),
    ("laptop", "Dell", "Inspiron 14", "mainstream", 59999, 58000, 59999,
     16, 512, "14\" FHD IPS", "medium",
     ["coding", "productivity", "daily_tasks"],
     ["Good value", "Comfortable keyboard", "Windows Hello"],
     ["Mediocre display", "Average speakers"],
     4.1, 8200, False, None, None),
    ("laptop", "Acer", "Aspire 7", "budget-gaming", 62999, 60000, 62999,
     16, 512, "15.6\" FHD 144Hz", "medium",
     ["gaming", "coding", "productivity"],
     ["RTX 4050", "144Hz display", "Upgradeable RAM"],
     ["Bulky", "Average battery", "Mediocre speakers"],
     4.1, 6800, False, None, None),
    ("laptop", "ASUS", "ROG Zephyrus G14", "premium-gaming", 149999, 145000, 149999,
     16, 1024, "14\" QHD+ 120Hz", "low",
     ["gaming", "video_editing", "creative"],
     ["RTX 4060", "AniMe Matrix LED", "Compact gaming"],
     ["Expensive", "Bottom exhaust gets hot"],
     4.6, 4200, True, 105000, "ASUS Certified"),
    ("laptop", "Lenovo", "ThinkPad E16 Gen 2", "business", 74999, 72000, 74999,
     16, 512, "16\" WUXGA IPS", "high",
     ["coding", "productivity", "data_science"],
     ["TrackPoint", "Spill-resistant keyboard", "MIL-STD-810H"],
     ["Integrated GPU", "Mediocre display"],
     4.3, 3800, False, None, None),
    ("laptop", "HP", "Victus 15", "budget-gaming", 64999, 60000, 64999,
     8, 512, "15.6\" FHD 144Hz", "medium",
     ["gaming", "coding", "productivity"],
     ["RTX 4050", "144Hz", "Affordable"],
     ["Plastic build", "Mediocre battery", "Loud fans"],
     4.0, 5600, False, None, None),
    ("laptop", "Apple", "MacBook Pro 14 M4 Pro", "premium", 199900, 199900, 199900,
     24, 512, "14.2\" Liquid Retina XDR", "low",
     ["video_editing", "coding", "data_science"],
     ["M4 Pro chip", "22hr battery", "ProMotion"],
     ["Very expensive", "Heavy for 14\""],
     4.8, 8900, False, None, None),
    ("laptop", "ASUS", "Vivobook 15", "budget", 39999, 38000, 39999,
     8, 512, "15.6\" FHD IPS", "high",
     ["daily_tasks", "productivity", "coding"],
     ["Affordable", "Decent keyboard", "Good port selection"],
     ["Mediocre display", "Average battery"],
     4.0, 11000, False, None, None),
    ("laptop", "Lenovo", "Legion 5i", "gaming", 99999, 95000, 99999,
     16, 1024, "16\" WQXGA 165Hz", "medium",
     ["gaming", "video_editing", "streaming"],
     ["RTX 4060", "MUX switch", "165Hz panel"],
     ["Heavy", "Average battery when gaming"],
     4.4, 6200, True, 72000, "Lenovo Certified"),
    ("laptop", "MSI", "Modern 14", "ultrabook", 49999, 47000, 49999,
     16, 512, "14\" FHD IPS", "medium",
     ["coding", "productivity", "daily_tasks"],
     ["Lightweight", "Good battery", "Fast charging"],
     ["Mediocre speakers", "No dedicated GPU"],
     4.1, 3400, False, None, None),
    ("laptop", "Acer", "Nitro V 15", "budget-gaming", 74999, 72000, 74999,
     16, 1024, "15.6\" FHD 144Hz", "medium",
     ["gaming", "coding", "streaming"],
     ["RTX 4050", "144Hz", "1TB storage"],
     ["Bulky", "Average build quality"],
     4.1, 4800, False, None, None),
    ("laptop", "Dell", "XPS 14", "premium", 134999, 130000, 134999,
     16, 512, "14.5\" FHD+ InfinityEdge", "low",
     ["coding", "creative", "productivity"],
     ["Stunning build", "Haptic trackpad", "Compact"],
     ["Expensive", "No SD card slot"],
     4.5, 3600, False, None, None),
    ("laptop", "HP", "ProBook 450 G10", "business", 52999, 50000, 52999,
     8, 512, "15.6\" FHD IPS", "high",
     ["productivity", "coding", "daily_tasks"],
     ["MIL-STD rated", "Good keyboard", "Manageable"],
     ["Integrated GPU", "Average display"],
     4.1, 2800, False, None, None),
    ("laptop", "Samsung", "Galaxy Book 4 Pro", "premium", 124999, 118000, 124999,
     16, 512, "14\" AMOLED 2X", "low",
     ["coding", "creative", "productivity"],
     ["AMOLED display", "Ultra-thin", "Samsung ecosystem"],
     ["Expensive", "Fragile hinges"],
     4.3, 2900, False, None, None),
    ("laptop", "Lenovo", "IdeaPad Gaming 3", "budget-gaming", 59999, 57000, 59999,
     8, 512, "15.6\" FHD 120Hz", "medium",
     ["gaming", "coding", "daily_tasks"],
     ["RTX 3050", "120Hz", "Upgradeable"],
     ["Mediocre battery", "Loud under load"],
     4.0, 7200, False, None, None),
    ("laptop", "Framework", "16", "enthusiast", 159999, 159999, 159999,
     32, 1024, "16\" 2560x1600", "low",
     ["coding", "Linux", "repairability"],
     ["Fully modular", "No e-waste", "Powerful"],
     ["Expensive", "Availability issues in India"],
     4.6, 1200, False, None, None),
    ("laptop", "ASUS", "Zenbook 14 OLED", "ultrabook", 84999, 82000, 84999,
     16, 512, "14\" 2.8K OLED", "low",
     ["coding", "creative", "productivity"],
     ["OLED display", "Lightweight", "Good battery"],
     ["Limited ports", "Soldered RAM"],
     4.4, 3100, False, None, None),

    # ── Audio (16) ───────────────────────────────────────────────────────
    ("audio", "Sony", "WH-1000XM5", "premium", 25999, 26000, 30000,
     None, None, "Over-ear", "low",
     ["anc", "remote_work", "travel"],
     ["Industry-leading ANC", "LDAC", "30hr battery"],
     ["Non-foldable", "Sensitive to wind noise"],
     4.7, 45000, True, 18000, "Amazon Renewed"),
    ("audio", "OnePlus", "Buds Pro 3", "mid-range", 10999, 11000, 10500,
     None, None, "In-ear TWS", "low",
     ["anc", "daily_tasks", "music"],
     ["Good ANC", "LHDC codec", "Spatial audio"],
     ["Average mic", "App required"],
     4.2, 8700, False, None, None),
    ("audio", "Anker", "Soundcore Space Q45", "budget-anc", 6999, 7000, 7000,
     None, None, "Over-ear", "very_low",
     ["anc", "budget", "daily_tasks"],
     ["Best ANC under 7k", "50hr battery", "LDAC"],
     ["Plasticky build", "Average soundstage"],
     4.1, 19000, False, None, None),
    ("audio", "Sony", "WF-1000XM5", "premium", 24999, 24000, 27999,
     None, None, "In-ear TWS", "low",
     ["anc", "travel", "music"],
     ["Best TWS ANC", "Hi-Res Audio", "Compact case"],
     ["Expensive", "Touch controls inconsistent"],
     4.6, 28000, True, 17000, "Amazon Renewed"),
    ("audio", "Apple", "AirPods Pro 2", "premium", 24900, 23500, 24900,
     None, None, "In-ear TWS", "low",
     ["anc", "daily_tasks", "apple_ecosystem"],
     ["Adaptive ANC", "Spatial Audio", "Find My integration"],
     ["Best with iPhone", "Non-replaceable tips"],
     4.7, 52000, False, None, None),
    ("audio", "Sennheiser", "Momentum 4", "premium", 29999, 28000, 34999,
     None, None, "Over-ear", "low",
     ["music", "remote_work", "anc"],
     ["Audiophile sound", "60hr battery", "Smart Pause"],
     ["Bulky design", "Average ANC"],
     4.5, 6800, True, 20000, "Amazon Renewed"),
    ("audio", "JBL", "Tune 770NC", "budget", 5999, 5500, 5999,
     None, None, "Over-ear", "very_low",
     ["anc", "budget", "daily_tasks"],
     ["Good for price", "70hr battery", "Foldable"],
     ["Average ANC", "Plasticky build"],
     4.0, 12000, False, None, None),
    ("audio", "Samsung", "Galaxy Buds FE", "budget", 5999, 5500, 6999,
     None, None, "In-ear TWS", "very_low",
     ["anc", "samsung_ecosystem", "budget"],
     ["Good ANC for price", "Comfortable fit"],
     ["Average battery", "Samsung-only extras"],
     4.0, 8400, False, None, None),
    ("audio", "Nothing", "Ear (2)", "mid-range", 9999, 9500, 9999,
     None, None, "In-ear TWS", "low",
     ["music", "anc", "daily_tasks"],
     ["Transparent design", "Good ANC", "Hi-Res certified"],
     ["Average mic", "Case scratches easily"],
     4.1, 5200, False, None, None),
    ("audio", "Bose", "QuietComfort Ultra", "premium", 34999, 34000, 34999,
     None, None, "Over-ear", "low",
     ["anc", "travel", "remote_work"],
     ["Best ANC", "Immersive Audio", "Comfortable"],
     ["Expensive", "No LDAC"],
     4.7, 9800, False, None, None),
    ("audio", "Jabra", "Elite 10 Gen 2", "premium", 19999, 19000, 19999,
     None, None, "In-ear TWS", "low",
     ["anc", "calls", "music"],
     ["Dolby head tracking", "Comfortable", "Good calls"],
     ["Expensive", "Average ANC"],
     4.3, 4600, False, None, None),
    ("audio", "Shure", "AONIC 50 Gen 2", "premium", 29999, 28000, 34999,
     None, None, "Over-ear", "low",
     ["music", "remote_work", "studio"],
     ["Studio quality", "Detachable cable", "45hr battery"],
     ["Heavy", "Bulky carry case"],
     4.5, 3200, False, None, None),
    ("audio", "Marshall", "Major IV", "mid-range", 14999, 14000, 14999,
     None, None, "On-ear", "low",
     ["music", "daily_tasks", "style"],
     ["Iconic design", "80hr battery", "Wireless charging"],
     ["Tight on-ear fit", "No ANC"],
     4.2, 7800, False, None, None),
    ("audio", "Realme", "Buds Air 5 Pro", "budget", 4999, 4500, 4999,
     None, None, "In-ear TWS", "medium",
     ["anc", "budget", "daily_tasks"],
     ["LDAC", "Good ANC for price", "50hr total battery"],
     ["Average mic", "Mediocre app"],
     3.9, 6200, False, None, None),
    ("audio", "Sony", "WH-1000XM4", "previous-gen", 22999, 16000, 28999,
     None, None, "Over-ear", "low",
     ["anc", "remote_work", "travel"],
     ["Proven ANC", "30hr battery", "Speak-to-Chat"],
     ["Older model", "Non-foldable"],
     4.6, 62000, True, 12000, "Amazon Renewed"),
    ("audio", "Edifier", "Stax Spirit S3", "audiophile", 17999, 17000, 17999,
     None, None, "Planar magnetic", "low",
     ["music", "audiophile", "wired_wireless"],
     ["Planar magnetic", "aptX HD", "42hr battery"],
     ["Niche appeal", "No ANC"],
     4.4, 2100, False, None, None),

    # ── Video / TVs (14) ─────────────────────────────────────────────────
    ("video", "LG", "55\" B4 OLED", "premium", 119999, 120000, 115000,
     None, None, "55\" OLED 4K 120Hz", "low",
     ["gaming", "streaming", "home_theater"],
     ["Perfect blacks", "120Hz HDMI 2.1", "webOS"],
     ["Burn-in risk", "Premium pricing"],
     4.7, 11200, False, None, None),
    ("video", "TCL", "55\" C655 QLED", "mid-range", 54999, 55000, 52000,
     None, None, "55\" QLED 4K 144Hz", "low",
     ["streaming", "daily_use", "gaming"],
     ["Bright panel", "Google TV", "Dolby Vision"],
     ["Mediocre local dimming", "Average motion"],
     4.2, 6500, False, None, None),
    ("video", "Hisense", "55\" U7K Mini-LED", "value-premium", 64999, 65000, 68000,
     None, None, "55\" Mini-LED 4K 144Hz", "very_low",
     ["streaming", "gaming", "home_theater"],
     ["Mini-LED backlight", "Below baseline", "144Hz gaming"],
     ["Less brand recognition", "Limited service network"],
     4.3, 3200, False, None, None),
    ("video", "Samsung", "55\" S90D OLED", "premium", 139999, 135000, 139999,
     None, None, "55\" QD-OLED 4K 144Hz", "low",
     ["gaming", "streaming", "home_theater"],
     ["QD-OLED panel", "144Hz", "Samsung Gaming Hub"],
     ["Expensive", "No Dolby Vision"],
     4.6, 5800, False, None, None),
    ("video", "Xiaomi", "55\" QLED X Pro", "budget", 34999, 33000, 34999,
     None, None, "55\" QLED 4K 60Hz", "medium",
     ["streaming", "daily_use", "budget"],
     ["Affordable QLED", "Patchwall UI", "Dolby Vision"],
     ["60Hz only", "Mediocre upscaling"],
     4.0, 8900, False, None, None),
    ("video", "LG", "43\" UR7500", "budget", 32999, 31000, 32999,
     None, None, "43\" UHD 4K", "very_low",
     ["streaming", "daily_use", "bedroom"],
     ["webOS", "Good for price", "AirPlay"],
     ["60Hz only", "Mediocre blacks"],
     4.0, 7200, False, None, None),
    ("video", "Sony", "55\" Bravia 7", "premium", 149999, 145000, 149999,
     None, None, "55\" Mini-LED 4K 120Hz", "low",
     ["streaming", "home_theater", "gaming"],
     ["X-Anti Reflection", "XR Processor", "Bravia Core"],
     ["Expensive", "No Dolby Vision gaming"],
     4.5, 3800, False, None, None),
    ("video", "Samsung", "43\" Crystal 4K", "budget", 29999, 28000, 29999,
     None, None, "43\" UHD 4K", "low",
     ["daily_use", "streaming", "bedroom"],
     ["Affordable", "Tizen OS", "Slim design"],
     ["60Hz only", "Mediocre viewing angles"],
     3.9, 12000, False, None, None),
    ("video", "TCL", "65\" C755 Mini-LED", "mainstream", 69999, 68000, 69999,
     None, None, "65\" Mini-LED 4K 144Hz", "low",
     ["gaming", "streaming", "home_theater"],
     ["Mini-LED at 65\"", "144Hz", "Google TV"],
     ["Mediocre local dimming", "Average speakers"],
     4.2, 4200, False, None, None),
    ("video", "Hisense", "65\" U8N", "value-premium", 89999, 87000, 89999,
     None, None, "65\" Mini-LED 4K 144Hz", "very_low",
     ["gaming", "streaming", "home_theater"],
     ["Very bright panel", "144Hz", "Value king"],
     ["Mediocre OS", "Average upscaling"],
     4.3, 2800, False, None, None),
    ("video", "Samsung", "55\" The Frame", "lifestyle", 84999, 82000, 84999,
     None, None, "55\" QLED 4K", "medium",
     ["art_mode", "streaming", "living_room"],
     ["Art display mode", "Matte finish", "Slim wall mount"],
     ["Art subscription extra", "60Hz"],
     4.2, 5600, False, None, None),
    ("video", "LG", "65\" C4 OLED", "premium", 179999, 175000, 179999,
     None, None, "65\" OLED 4K 120Hz", "low",
     ["gaming", "streaming", "home_theater"],
     ["OLED evo", "4x HDMI 2.1", "WebOS 24"],
     ["Very expensive", "Burn-in risk"],
     4.7, 4200, False, None, None),
    ("video", "Xiaomi", "43\" TV A Pro", "budget", 22999, 21500, 22999,
     None, None, "43\" UHD 4K", "low",
     ["daily_use", "streaming", "budget"],
     ["Very affordable", "Google TV", "Metal frame"],
     ["60Hz", "Mediocre sound"],
     3.9, 14000, False, None, None),
    ("video", "Vu", "55\" Masterpiece Glo", "mainstream", 42999, 41000, 42999,
     None, None, "55\" QLED 4K 60Hz", "low",
     ["streaming", "daily_use", "home_theater"],
     ["JBL speakers", "QLED panel", "Ambient Mode"],
     ["60Hz only", "Average remote"],
     4.0, 3600, False, None, None),

    # ── Memory / Storage (16) ────────────────────────────────────────────
    ("memory", "Crucial", "T500 1TB NVMe Gen4", "mainstream", 8499, 8500, 7000,
     None, 1024, "M.2 NVMe Gen4", "high",
     ["video_editing", "gaming", "fast_storage"],
     ["Gen4 speeds", "DRAM cache", "Reliable brand"],
     ["Inflated above baseline"],
     4.5, 21000, False, None, None),
    ("memory", "Lexar", "NM790 1TB NVMe", "budget", 5799, 5800, 5500,
     None, 1024, "M.2 NVMe Gen4", "medium",
     ["daily_use", "gaming", "budget_storage"],
     ["Good price per GB", "Respectable Gen4 speeds"],
     ["DRAM-less", "Lesser warranty support"],
     4.2, 9400, False, None, None),
    ("memory", "Samsung", "990 EVO 1TB", "mainstream", 8999, 9000, 7500,
     None, 1024, "M.2 NVMe Gen4x2", "high",
     ["video_editing", "gaming"],
     ["Samsung reliability", "PCIe 4x2 hybrid"],
     ["Priced above baseline", "Not fastest Gen4"],
     4.4, 14000, False, None, None),
    ("memory", "WD", "Black SN850X 2TB", "premium", 14999, 14000, 12999,
     None, 2048, "M.2 NVMe Gen4", "high",
     ["video_editing", "gaming", "fast_storage"],
     ["Top-tier Gen4", "DRAM cache", "2TB capacity"],
     ["Inflated above baseline"],
     4.6, 11000, False, None, None),
    ("memory", "Samsung", "980 Pro 1TB", "previous-gen", 9999, 7500, 9999,
     None, 1024, "M.2 NVMe Gen4", "low",
     ["gaming", "fast_storage", "productivity"],
     ["Below baseline", "Proven reliability", "DRAM cache"],
     ["Older model", "Gen4 not newest"],
     4.5, 28000, True, 5500, "Amazon Renewed"),
    ("memory", "Crucial", "MX500 2TB SATA", "budget", 11999, 12000, 10000,
     None, 2048, "2.5\" SATA SSD", "high",
     ["storage_upgrade", "laptop", "budget"],
     ["SATA reliability", "Good for old laptops"],
     ["SATA speeds", "Above baseline"],
     4.3, 16000, False, None, None),
    ("memory", "Kingston", "NV2 2TB NVMe", "budget", 9999, 9500, 9000,
     None, 2048, "M.2 NVMe Gen4", "medium",
     ["budget_storage", "gaming", "daily_use"],
     ["Affordable 2TB", "Gen4 speeds"],
     ["DRAM-less", "QLC write speeds"],
     4.1, 7800, False, None, None),
    ("memory", "Samsung", "990 Pro 2TB", "premium", 19999, 19000, 16999,
     None, 2048, "M.2 NVMe Gen4", "high",
     ["video_editing", "gaming", "workstation"],
     ["Top Gen4 performance", "DRAM cache", "Samsung reliability"],
     ["Above baseline pricing"],
     4.7, 8200, False, None, None),
    ("memory", "Corsair", "MP600 Pro LPX 2TB", "mainstream", 15999, 15000, 13999,
     None, 2048, "M.2 NVMe Gen4", "high",
     ["gaming", "video_editing", "fast_storage"],
     ["High sequential speeds", "DRAM cache", "Low profile"],
     ["Above baseline"],
     4.5, 6400, False, None, None),
    ("memory", "WD", "Blue SN580 1TB", "budget", 6499, 6200, 6499,
     None, 1024, "M.2 NVMe Gen4", "medium",
     ["daily_use", "budget_storage", "laptop"],
     ["At baseline price", "Good for everyday", "Low power"],
     ["DRAM-less", "Not for heavy workloads"],
     4.2, 13000, False, None, None),
    ("memory", "Kingston", "Fury Beast 32GB DDR5", "mainstream", 8999, 8500, 7500,
     32, None, "DDR5-5600 DIMM", "high",
     ["ram_upgrade", "gaming", "productivity"],
     ["32GB capacity", "XMP 3.0", "Heat spreader"],
     ["DDR5 pricing inflated"],
     4.4, 5600, False, None, None),
    ("memory", "Corsair", "Vengeance 16GB DDR5", "budget", 4999, 4800, 4500,
     16, None, "DDR5-5200 DIMM", "medium",
     ["ram_upgrade", "daily_use", "budget_build"],
     ["Affordable DDR5", "Low profile"],
     ["Basic heatspreader"],
     4.2, 9200, False, None, None),
    ("memory", "G.Skill", "Trident Z5 64GB DDR5", "premium", 18999, 18500, 16999,
     64, None, "DDR5-6000 DIMM", "high",
     ["workstation", "video_editing", "content_creation"],
     ["64GB capacity", "High speed", "RGB"],
     ["Premium pricing", "Overkill for most"],
     4.6, 3200, False, None, None),
    ("memory", "Crucial", "P3 Plus 2TB NVMe", "budget", 10999, 10500, 9999,
     None, 2048, "M.2 NVMe Gen4", "medium",
     ["budget_storage", "gaming", "daily_use"],
     ["QLC for value", "Good for read-heavy"],
     ["QLC write degradation", "Above baseline"],
     4.0, 6800, False, None, None),
    ("memory", "Seagate", "FireCuda 530 1TB", "premium", 12999, 12500, 10999,
     None, 1024, "M.2 NVMe Gen4", "high",
     ["gaming", "video_editing", "workstation"],
     ["DRAM cache", "High endurance", "PlayStation validated"],
     ["Above baseline"],
     4.6, 5800, False, None, None),
    ("memory", "Samsung", "T7 Shield 2TB Portable", "mainstream", 14999, 14500, 13000,
     None, 2048, "USB 3.2 Gen2 Portable", "medium",
     ["portable_storage", "video_editing", "backup"],
     ["IP65 rated", "Fast USB speeds", "Compact"],
     ["USB limited speed", "Above baseline"],
     4.4, 7200, False, None, None),

    # ── Wearable (16) ────────────────────────────────────────────────────
    ("wearable", "Samsung", "Galaxy Watch 7", "mainstream", 27999, 28000, 27000,
     None, None, "1.3\" Super AMOLED", "low",
     ["health_tracking", "fitness", "notifications"],
     ["ECG + BIA sensors", "Wear OS 5", "Android ecosystem"],
     ["1.5-day battery", "Best with Samsung phones"],
     4.3, 7800, True, 19000, "Amazon Renewed"),
    ("wearable", "Fitbit", "Charge 6", "fitness-band", 13999, 14000, 13000,
     None, None, "AMOLED tracker", "very_low",
     ["fitness", "health_tracking"],
     ["7-day battery", "Google integration", "Excellent sensors"],
     ["Limited apps", "Fitbit Premium required for full features"],
     4.2, 5600, False, None, None),
    ("wearable", "Amazfit", "Balance", "budget-smart", 11999, 12000, 12000,
     None, None, "1.5\" AMOLED", "very_low",
     ["fitness", "daily_use", "budget"],
     ["14-day battery", "Built-in Alexa", "Great display"],
     ["Limited third-party apps"],
     4.1, 4200, False, None, None),
    ("wearable", "Apple", "Watch Series 10", "premium", 46900, 46900, 46900,
     None, None, "1.9\" OLED", "low",
     ["health_tracking", "fitness", "apple_ecosystem"],
     ["Crash Detection", "Sleep apnea detection", "Fast charging"],
     ["Best with iPhone", "1-day battery"],
     4.6, 15000, False, None, None),
    ("wearable", "Samsung", "Galaxy Watch Ultra", "premium", 64999, 64000, 64999,
     None, None, "1.5\" Super AMOLED", "low",
     ["fitness", "adventure", "health_tracking"],
     ["Titanium build", "100m water resistance", "7-day battery"],
     ["Very expensive", "Bulky"],
     4.4, 3200, False, None, None),
    ("wearable", "Garmin", "Venu 3", "premium", 44999, 43000, 44999,
     None, None, "1.4\" AMOLED", "low",
     ["fitness", "health_tracking", "daily_use"],
     ["14-day battery", "Body Battery", "Advanced sleep tracking"],
     ["Expensive", "Basic smart features"],
     4.5, 5800, False, None, None),
    ("wearable", "Amazfit", "T-Rex Ultra 2", "outdoor", 24999, 24000, 24999,
     None, None, "1.5\" AMOLED", "low",
     ["fitness", "outdoor", "adventure"],
     ["MIL-STD rated", "Dive computer", "GPS dual-band"],
     ["Bulky", "Average app ecosystem"],
     4.3, 2800, False, None, None),
    ("wearable", "OnePlus", "Watch 2", "mainstream", 22999, 22000, 22999,
     None, None, "1.43\" AMOLED", "low",
     ["fitness", "health_tracking", "daily_use"],
     ["Wear OS 5", "Dual-engine", "5-day battery"],
     ["Best with OnePlus", "Limited watch faces"],
     4.2, 3400, False, None, None),
    ("wearable", "Noise", "ColorFit Pro 5", "budget", 4999, 4500, 4999,
     None, None, "1.85\" AMOLED", "very_low",
     ["fitness", "daily_use", "budget"],
     ["Big display", "Bluetooth calling", "Affordable"],
     ["Average sensors", "Basic app"],
     3.9, 8200, False, None, None),
    ("wearable", "Apple", "Watch SE 2", "entry", 29900, 28000, 29900,
     None, None, "1.57\" OLED", "low",
     ["fitness", "health_tracking", "apple_ecosystem"],
     ["Affordable Apple Watch", "Crash Detection", "Family Setup"],
     ["No always-on display", "Older chipset"],
     4.3, 12000, False, None, None),
    ("wearable", "Huawei", "Watch GT 5 Pro", "mainstream", 29999, 28000, 29999,
     None, None, "1.43\" AMOLED", "low",
     ["fitness", "health_tracking", "daily_use"],
     ["14-day battery", "ECG", "Premium build"],
     ["No Google apps", "Limited NFC payments"],
     4.3, 4600, False, None, None),
    ("wearable", "Samsung", "Galaxy Fit 3", "budget", 5999, 5500, 5999,
     None, None, "1.6\" AMOLED", "very_low",
     ["fitness", "daily_use", "budget"],
     ["13-day battery", "Slim design", "Water resistant"],
     ["Basic notifications", "Samsung-only extras"],
     4.1, 3800, False, None, None),
    ("wearable", "Garmin", "Forerunner 265", "running", 39999, 38000, 39999,
     None, None, "1.3\" AMOLED", "low",
     ["running", "fitness", "health_tracking"],
     ["Training readiness", "AMOLED", "13-day battery"],
     ["Expensive", "No LTE option"],
     4.5, 4200, False, None, None),
    ("wearable", "Amazfit", "GTR 4", "mainstream", 15999, 15000, 15999,
     None, None, "1.43\" AMOLED", "low",
     ["fitness", "health_tracking", "daily_use"],
     ["14-day battery", "Alexa", "Bluetooth calling"],
     ["Average GPS", "Mediocre app store"],
     4.1, 5400, False, None, None),
    ("wearable", "Fire-Boltt", "Invincible Plus", "budget", 3999, 3500, 3999,
     None, None, "1.43\" AMOLED", "very_low",
     ["daily_use", "budget", "style"],
     ["Big display", "Bluetooth calling", "Ultra affordable"],
     ["Inaccurate sensors", "Basic build"],
     3.7, 11000, False, None, None),
    ("wearable", "Apple", "Watch Ultra 2", "premium-rugged", 89900, 89000, 89900,
     None, None, "1.93\" OLED", "low",
     ["adventure", "fitness", "diving"],
     ["Titanium", "Precision dual-frequency GPS", "Action button"],
     ["Very expensive", "Bulky for small wrists"],
     4.7, 6800, False, None, None),
]


# ─── Seed functions ───────────────────────────────────────────────────────────

def seed_chipflation(cur):
    """Seed chipflation_index if empty."""
    cur.execute("SELECT COUNT(*) FROM chipflation_index")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  ↳ chipflation_index already has {count} rows — skipping.")
        return 0

    for comp, spot, mom, yoy, source in CHIPFLATION_SEED:
        cur.execute(
            """INSERT INTO chipflation_index
               (component_type, spot_price_usd, mom_growth_pct, yoy_growth_pct, source)
               VALUES (%s, %s, %s, %s, %s)""",
            (comp, spot, mom, yoy, source),
        )
    print(f"  ↳ Seeded {len(CHIPFLATION_SEED)} chipflation_index rows.")
    return len(CHIPFLATION_SEED)


def seed_sale_events(cur):
    """Seed sale_events if empty."""
    cur.execute("SELECT COUNT(*) FROM sale_events")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  ↳ sale_events already has {count} rows — skipping.")
        return 0

    for name, platform, start, end, disc, cats, notes in SALE_EVENTS_SEED:
        cur.execute(
            """INSERT INTO sale_events
               (event_name, platform, start_date, end_date,
                typical_discount_pct, categories, notes)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (name, platform, start, end, disc, cats, notes),
        )
    print(f"  ↳ Seeded {len(SALE_EVENTS_SEED)} sale_events rows.")
    return len(SALE_EVENTS_SEED)


def seed_gadgets(cur):
    """Seed gadgets table if empty. Inserts all products from GADGETS_SEED."""
    cur.execute("SELECT COUNT(*) FROM gadgets")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  ↳ gadgets already has {count} rows — skipping.")
        return 0

    for row in GADGETS_SEED:
        cur.execute(
            """INSERT INTO gadgets
               (category, brand, model_name, tier, base_msrp, current_price,
                historical_baseline, ram_gb, storage_gb, display_spec,
                chipflation_risk, use_cases, pros, cons, rating, review_count,
                refurb_available, refurb_price, refurb_source)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            row,
        )
    print(f"  ↳ Seeded {len(GADGETS_SEED)} gadgets.")
    return len(GADGETS_SEED)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        print("Usage: DATABASE_URL='postgresql://...' python scripts/migrate_to_neon.py")
        sys.exit(1)

    # Mask password in output
    safe_url = database_url.split("@")[-1] if "@" in database_url else database_url
    print(f"Connecting to: {safe_url}")

    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        conn.autocommit = False
    except psycopg2.OperationalError as e:
        print(f"ERROR: Could not connect to database: {e}")
        sys.exit(1)

    try:
        cur = conn.cursor()

        # ── Create tables ────────────────────────────────────────────────
        print("\n1. Creating tables…")
        cur.execute(SCHEMA_SQL)
        print("  ✓ All tables created (IF NOT EXISTS).")

        # ── Seed data ────────────────────────────────────────────────────
        print("\n2. Seeding data…")
        seed_chipflation(cur)
        seed_sale_events(cur)
        seed_gadgets(cur)

        # ── Commit ───────────────────────────────────────────────────────
        conn.commit()
        print("\n✅ Migration complete!")

        # ── Summary ──────────────────────────────────────────────────────
        print("\nTable row counts:")
        for table in ("gadgets", "chipflation_index", "user_devices",
                       "emi_audit_log", "price_history", "sale_events"):
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            cnt = cur.fetchone()[0]
            print(f"  {table}: {cnt} rows")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed — {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
