-- AIDE-OS PostgreSQL Schema v4.0.0
-- Run: psql -U aideuser -d aideosdb -f schema.sql

-- Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Gadgets Master Catalogue ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gadgets (
    gadget_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category        VARCHAR(20) NOT NULL CHECK (category IN ('mobile','laptop','audio','video','memory','wearable')),
    brand           VARCHAR(60) NOT NULL,
    model_name      VARCHAR(120) NOT NULL,
    tier            VARCHAR(40),                        -- flagship, mid-range, budget, premium
    base_msrp       NUMERIC(12, 2) NOT NULL,
    current_price   NUMERIC(12, 2) NOT NULL,
    historical_baseline NUMERIC(12, 2) NOT NULL,
    ram_gb          SMALLINT,
    storage_gb      INT,
    display_spec    VARCHAR(120),
    chipflation_risk VARCHAR(20) DEFAULT 'medium',      -- very_low, low, medium, high
    use_cases       TEXT[],                             -- e.g. ARRAY['gaming','coding']
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

CREATE INDEX idx_gadgets_category ON gadgets(category);
CREATE INDEX idx_gadgets_price    ON gadgets(current_price);

-- ─── Chipflation Spot Price Log ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chipflation_index (
    index_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_type  VARCHAR(50) NOT NULL,               -- DRAM_DDR5, NAND_FLASH, LPDDR5X, HBM
    spot_price_usd  NUMERIC(10, 4) NOT NULL,
    mom_growth_pct  NUMERIC(6, 2) NOT NULL,
    yoy_growth_pct  NUMERIC(6, 2),
    source          VARCHAR(80),                        -- TrendForce, DRAMeXchange, manual
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chipflation_component ON chipflation_index(component_type);
CREATE INDEX idx_chipflation_time      ON chipflation_index(recorded_at DESC);

-- ─── User Devices (telemetry submissions) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS user_devices (
    device_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          VARCHAR(64),                    -- anonymous session token
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
    source      VARCHAR(80),                            -- Amazon, Flipkart, Croma
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_price_history_gadget ON price_history(gadget_id, recorded_at DESC);

-- ─── Sale Event Calendar ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sale_events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name      VARCHAR(120) NOT NULL,
    platform        VARCHAR(60),                        -- Amazon, Flipkart, All
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    typical_discount_pct NUMERIC(4, 1),
    categories      TEXT[],                             -- which categories benefit most
    notes           TEXT
);

-- ─── Seed Data ──────────────────────────────────────────────────────────────

INSERT INTO chipflation_index (component_type, spot_price_usd, mom_growth_pct, yoy_growth_pct, source) VALUES
    ('LPDDR5X',     3.85, 4.20,  18.50, 'TrendForce'),
    ('DDR5_SODIMM', 4.12, 3.80,  22.10, 'TrendForce'),
    ('NAND_3D_TLC',  0.065, 5.10, 24.30, 'DRAMeXchange'),
    ('HBM3E',       18.40, 2.10,  41.00, 'TrendForce'),
    ('LPDDR4X',      2.20, 1.50,   8.20, 'TrendForce');

INSERT INTO sale_events (event_name, platform, start_date, end_date, typical_discount_pct, categories, notes) VALUES
    ('Big Billion Days',       'Flipkart',  '2026-10-01', '2026-10-06', 20.0, ARRAY['mobile','laptop','audio','video','wearable'], 'Biggest sale of the year'),
    ('Great Indian Festival',  'Amazon',    '2026-10-01', '2026-10-06', 18.0, ARRAY['mobile','laptop','audio','video','memory'],   'Runs concurrent with Big Billion'),
    ('Republic Day Sale',      'All',       '2026-01-20', '2026-01-26', 12.0, ARRAY['mobile','laptop','audio'],                   'Good for smartphones'),
    ('Independence Day Sale',  'All',       '2026-08-10', '2026-08-15', 10.0, ARRAY['mobile','laptop'],                          'Back-to-college overlap'),
    ('Prime Day',              'Amazon',    '2026-07-16', '2026-07-17', 15.0, ARRAY['audio','memory','wearable'],                 'Flash deals on accessories'),
    ('New Year Sale',          'All',       '2026-01-01', '2026-01-05', 10.0, ARRAY['video','wearable'],                         'TV and smartwatch deals'),
    ('Black Friday',           'All',       '2026-11-27', '2026-11-30', 22.0, ARRAY['laptop','mobile','audio','video','memory'],  'Best laptop deals'),
    ('Back to College',        'All',       '2026-07-01', '2026-08-31', 12.0, ARRAY['laptop','mobile'],                          'Student discount stacking period');

INSERT INTO gadgets
    (category, brand, model_name, tier, base_msrp, current_price, historical_baseline,
     ram_gb, storage_gb, display_spec, chipflation_risk, use_cases, pros, cons,
     rating, review_count, refurb_available, refurb_price, refurb_source)
VALUES
    ('mobile','Samsung','Galaxy S25','flagship',79999,80000,75000,
     12,256,'120Hz Dynamic AMOLED 2X','medium',
     ARRAY['gaming','multitasking','photography'],
     ARRAY['Best-in-class camera','7 years OS updates','Compact form'],
     ARRAY['Premium pricing','No charger in box'],
     4.5,12400,true,55000,'Amazon Renewed / Samsung Certified'),

    ('mobile','Nothing','Phone 4(a)','mid-range',29999,30000,27000,
     12,256,'120Hz AMOLED','low',
     ARRAY['daily_tasks','social_media','gaming'],
     ARRAY['Unique design','Clean Android','Great value'],
     ARRAY['Limited accessories','No IP rating'],
     4.3,5800,false,null,null),

    ('mobile','Samsung','Galaxy S23','previous-gen',69999,52000,70000,
     8,256,'120Hz AMOLED','low',
     ARRAY['gaming','multitasking','daily_tasks'],
     ARRAY['Proven reliability','Below-baseline pricing','Excellent camera'],
     ARRAY['Older chipset','Shorter OS support window'],
     4.4,28000,true,38000,'Amazon Renewed'),

    ('mobile','OnePlus','11R','upper-mid',41999,40000,42000,
     16,256,'120Hz AMOLED','low',
     ARRAY['gaming','multitasking'],
     ARRAY['Below baseline deal','100W fast charging','OxygenOS'],
     ARRAY['No wireless charging','Plastic back'],
     4.3,9200,true,28000,'Cashify / Amazon Renewed'),

    ('laptop','Lenovo','IdeaPad Slim 5','mainstream',67999,68000,60000,
     16,512,'14" FHD IPS','high',
     ARRAY['coding','data_science','productivity'],
     ARRAY['16GB DDR5','Good keyboard','Decent build'],
     ARRAY['Mediocre battery','Audible fans under load'],
     4.2,7600,true,48000,'Lenovo Certified Refurbished'),

    ('laptop','ASUS','ExpertBook P1','business',71999,72000,65000,
     16,512,'15.6" FHD','high',
     ARRAY['coding','productivity','data_science'],
     ARRAY['Military-grade durability','Long battery','Business warranty'],
     ARRAY['Heavier than ultrabooks','Integrated GPU only'],
     4.4,3200,false,null,null),

    ('laptop','Apple','MacBook Air M4','premium',109999,110000,105000,
     16,512,'13.6" Liquid Retina','low',
     ARRAY['video_editing','creative','coding'],
     ARRAY['Best performance per watt','18hr battery','Fanless'],
     ARRAY['Premium price','Limited ports'],
     4.8,22000,true,85000,'Apple Certified Refurbished'),

    ('audio','Sony','WH-1000XM5','premium',25999,26000,30000,
     null,null,'Over-ear','low',
     ARRAY['anc','remote_work','travel'],
     ARRAY['Industry-leading ANC','LDAC','30hr battery'],
     ARRAY['Non-foldable','Sensitive to wind noise'],
     4.7,45000,true,18000,'Amazon Renewed'),

    ('audio','OnePlus','Buds Pro 3','mid-range',10999,11000,10500,
     null,null,'In-ear TWS','low',
     ARRAY['anc','daily_tasks','music'],
     ARRAY['Good ANC','LHDC codec','Spatial audio'],
     ARRAY['Average mic','App required'],
     4.2,8700,false,null,null),

    ('audio','Anker','Soundcore Space Q45','budget-anc',6999,7000,7000,
     null,null,'Over-ear','very_low',
     ARRAY['anc','budget','daily_tasks'],
     ARRAY['Best ANC under 7k','50hr battery','LDAC'],
     ARRAY['Plasticky build','Average soundstage'],
     4.1,19000,false,null,null),

    ('video','LG','55" B4 OLED','premium',119999,120000,115000,
     null,null,'55" OLED 4K 120Hz','low',
     ARRAY['gaming','streaming','home_theater'],
     ARRAY['Perfect blacks','120Hz HDMI 2.1','webOS'],
     ARRAY['Burn-in risk','Premium pricing'],
     4.7,11200,false,null,null),

    ('video','TCL','55" C655 QLED','mid-range',54999,55000,52000,
     null,null,'55" QLED 4K 144Hz','low',
     ARRAY['streaming','daily_use','gaming'],
     ARRAY['Bright panel','Google TV','Dolby Vision'],
     ARRAY['Mediocre local dimming','Average motion'],
     4.2,6500,false,null,null),

    ('video','Hisense','55" U7K Mini-LED','value-premium',64999,65000,68000,
     null,null,'55" Mini-LED 4K 144Hz','very_low',
     ARRAY['streaming','gaming','home_theater'],
     ARRAY['Mini-LED backlight','Below baseline','144Hz gaming'],
     ARRAY['Less brand recognition','Limited service network'],
     4.3,3200,false,null,null),

    ('memory','Crucial','T500 1TB NVMe Gen4','mainstream',8499,8500,7000,
     null,1024,'M.2 NVMe Gen4','high',
     ARRAY['video_editing','gaming','fast_storage'],
     ARRAY['Gen4 speeds','DRAM cache','Reliable brand'],
     ARRAY['Inflated above baseline'],
     4.5,21000,false,null,null),

    ('memory','Lexar','NM790 1TB NVMe','budget',5799,5800,5500,
     null,1024,'M.2 NVMe Gen4','medium',
     ARRAY['daily_use','gaming','budget_storage'],
     ARRAY['Good price per GB','Respectable Gen4 speeds'],
     ARRAY['DRAM-less','Lesser warranty support'],
     4.2,9400,false,null,null),

    ('memory','Samsung','990 EVO 1TB','mainstream',8999,9000,7500,
     null,1024,'M.2 NVMe Gen4x2','high',
     ARRAY['video_editing','gaming'],
     ARRAY['Samsung reliability','PCIe 4x2 hybrid'],
     ARRAY['Priced above baseline','Not fastest Gen4'],
     4.4,14000,false,null,null),

    ('wearable','Samsung','Galaxy Watch 7','mainstream',27999,28000,27000,
     null,null,'1.3" Super AMOLED','low',
     ARRAY['health_tracking','fitness','notifications'],
     ARRAY['ECG + BIA sensors','Wear OS 5','Android ecosystem'],
     ARRAY['1.5-day battery','Best with Samsung phones'],
     4.3,7800,true,19000,'Amazon Renewed'),

    ('wearable','Fitbit','Charge 6','fitness-band',13999,14000,13000,
     null,null,'AMOLED tracker','very_low',
     ARRAY['fitness','health_tracking'],
     ARRAY['7-day battery','Google integration','Excellent sensors'],
     ARRAY['Limited apps','Fitbit Premium required for full features'],
     4.2,5600,false,null,null),

    ('wearable','Amazfit','Balance','budget-smart',11999,12000,12000,
     null,null,'1.5" AMOLED','very_low',
     ARRAY['fitness','daily_use','budget'],
     ARRAY['14-day battery','Built-in Alexa','Great display'],
     ARRAY['Limited third-party apps'],
     4.1,4200,false,null,null);
