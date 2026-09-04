<div align="center">

# ⚡ AIDE-OS

**Omni-Gadget AI Dynamic Pricing Engine, Longevity Predictor & Purchase Decision System**

*AI-Driven Electronic Device Ecosystem — Open Source*

[![Version](https://img.shields.io/badge/version-4.0.0--PROD-6366f1?style=flat-square)](.)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776ab?style=flat-square&logo=python&logoColor=white)](.)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](.)
[![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square&logo=react&logoColor=black)](.)
[![Vite](https://img.shields.io/badge/Vite-6-646cff?style=flat-square&logo=vite&logoColor=white)](.)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)](.)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?style=flat-square&logo=docker&logoColor=white)](.)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](.)

<br/>

[![Deploy Backend to SnapDeploy](https://snapdeploy.dev/button.svg)](https://snapdeploy.dev/new)
[![Deploy Frontend to Vercel](https://vercel.com/button)](https://vercel.com/new)

> **Beat chipflation. Know when to buy, when to hold, and what your "No-Cost EMI" actually costs.**

</div>

---

## 📋 Table of Contents

1. [Problem Statement](#-problem-statement)
2. [Core Engine Modules](#-core-engine-modules)
3. [Mathematical Formulations](#-mathematical-formulations)
4. [System Architecture](#-system-architecture)
5. [Project Structure](#-project-structure)
6. [Zero-Cost Deployment](#-zero-cost-deployment-0-investment)
7. [Environment Variables](#-environment-variables)
8. [API Reference](#-api-reference)
9. [Test Results](#-test-results)
10. [Module Scoring](#-module-scoring)
11. [Technology Stack](#-technology-stack)
12. [Supported Categories](#-supported-categories)
13. [Business Model](#-business-model)
14. [Live Demo](#-live-demo)
15. [Contributing](#-contributing)
16. [What's Next](#-whats-next)
17. [License](#-license)

---

## 🔍 Problem Statement

### The "Chipflation" Phenomenon

The exponential growth of enterprise AI infrastructure has caused a structural shift in global semiconductor manufacturing. Foundry leaders (TSMC, Samsung, SK Hynix, Micron) have reallocated capacity toward high-margin AI chips and High-Bandwidth Memory (HBM), starving consumer-grade silicon of supply.

```
┌─────────────────────────────────────────────────────────────┐
│                  UPSTREAM SILICON SUPPLY                    │
│  TSMC / Samsung / SK Hynix → Enterprise AI Chips & HBM      │
└──────────────────────────────┬──────────────────────────────┘
                               │ capacity diverted
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  COMPONENT COST INFLATION                   │
│   LPDDR5X +18.5% YoY  •  DDR5 +22.1% YoY  •  NAND +24.3%  │
└──────────────────────────────┬──────────────────────────────┘
                               │ passed to retail
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               CONSUMER ELECTRONICS IMPACT                   │
│  Mobiles · Laptops · Audio · Video · Storage · Wearables    │
│  Inflated prices  •  Spec downgrades  •  Poor value timing  │
└─────────────────────────────────────────────────────────────┘
```

**AIDE-OS** solves consumer purchasing friction by combining supply-chain analytics, device diagnostics, intelligent recommendations, and transparent financial math into a single open-source decision engine.

---

## 🃏 Core Engine Modules

> Each module is an independent engine callable via REST. They compose into the `/full-decision` master endpoint.

<table>
<thead>
  <tr>
    <th width="50%">Module</th>
    <th width="50%">Module</th>
  </tr>
</thead>
<tbody>
<tr>
<td valign="top">

### 🔋 Module 6 — URL Engine
**Useful Remaining Life Calculator**

Computes how many years of practical life remain in current hardware before performance degrades below acceptable limits.

| Input | Description |
|-------|-------------|
| `battery_health_pct` | Current max capacity vs. design |
| `storage_health_pct` | TBW wear factor |
| `age_months` | Operational age |
| `physical_condition` | Normalized 0.0 – 1.0 |

**Output:** `HOLD_CURRENT_DEVICE` · `CONSIDER_REPLACEMENT` · `REPLACE_IMMEDIATELY`

</td>
<td valign="top">

### 📈 Module 2 — Chipflation Engine
**Dynamic Buy-vs-Hold Decision Index**

Tracks upstream DRAM/NAND spot prices and calculates whether current retail prices are inflated beyond historical baselines.

| DI Range | Signal | Action |
|----------|--------|--------|
| `> 1.25` | Overpriced | Hold or buy refurbished |
| `0.95–1.25` | Moderate | Buy with cashback/EMI stack |
| `< 0.95` | Optimal | Buy now |

**Output:** `OVERPRICED_HOLD` · `BUY_WITH_CASHBACK_EMI` · `BUY_NOW`

</td>
</tr>
<tr>
<td valign="top">

### 🎯 Modules 3 & 4 — Recommender
**Requirement-Based Product Matcher**

Maps user workloads and budgets to the best-fit products. Simultaneously surfaces certified refurbished and previous-gen alternatives that deliver equivalent real-world performance at lower cost.

| Tier | Source |
|------|--------|
| Primary | New retail — best use-case match |
| Alternative | Cross-brand / previous-gen |
| Refurbished | Amazon Renewed · Cashify · OEM Certified |

**Output:** Ranked list with match score, value verdict, pros/cons, chipflation risk

</td>
<td valign="top">

### 💳 Module 7 — EMI Audit Engine
**True-Cost Hidden Charge Extractor**

Exposes what "No-Cost EMI" actually costs by decomposing every hidden fee that retailers and banks do not disclose upfront.

| Hidden Charge | Who Charges |
|---------------|-------------|
| Bank processing fee | Bank |
| 18% GST on processing fee | Government |
| **18% GST on interest component** | Government (never reimbursed) |
| Forgone instant UPI/cash discount | Seller |

**Output:** True effective outlay, monthly EMI breakdown, `PAY_UPFRONT_CASH` vs `EMI_ACCEPTABLE`

</td>
</tr>
</tbody>
</table>

---

## 📐 Mathematical Formulations

### URL Score

$$\text{URL Score (\%)} = \left( 0.35 \cdot \text{BH} + 0.25 \cdot \text{SH} + 0.25 \cdot \left(1 - \frac{\text{Age}}{\text{EOL}}\right) + 0.15 \cdot \text{Phys} \right) \times 100$$

$$\text{Remaining Years} = \text{Max Lifespan} \times \frac{\text{URL Score}}{100}$$

### Decision Index (DI)

$$\text{DI} = \frac{\text{CI} \times \text{Current Price}}{\text{Historical Baseline}} - \left(1 - \frac{\text{URL Score}}{100}\right) \times \text{Urgency Factor}$$

### True EMI Cost

$$\text{True Cost} = \text{MSRP} + \underbrace{\text{Processing Fee} + \text{GST}_{processing} + \text{GST}_{interest}}_{\text{bank charges}} + \underbrace{\text{Forgone Cash Discount}}_{\text{opportunity cost}} - \text{Exchange Bonus}$$

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT LAYER                              │
│  Target Specs & Budget  •  Device Telemetry  •  Financing Preferences   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA PROCESSING PIPELINE                         │
│                                                                         │
│   ┌──────────────────────────┐      ┌──────────────────────────────┐    │
│   │   Device Diagnostics     │      │   Market & Supply Chain      │    │
│   │  • Battery / TBW Wear    │      │  • E-Commerce Live Pricing   │    │
│   │  • Physical Condition    │      │  • DRAM / NAND Spot Prices   │    │
│   │  • OS EOL Proximity      │      │  • Bank EMI Terms & Fees     │    │
│   └─────────────┬────────────┘      └───────────────┬──────────────┘    │
│                 └──────────────────┬─────────────────┘                  │
│                                    ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐    │
│   │                  CENTRAL DECISION ENGINE                       │    │
│   │                                                                │    │
│   │  Module 6: Useful Remaining Life (URL) Calculator              │    │
│   │  Module 2: Chipflation Decision Index (DI)                     │    │
│   │  Module 3: Requirement-Based Product Recommender               │    │
│   │  Module 4: Refurbished & Alternative Matcher                   │    │
│   │  Module 7: True-Cost EMI & Hidden Charges Extractor            │    │
│   └────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT LAYER                                 │
│  Master Verdict  •  Product Picks  •  EMI Audit  •  Optimal Buy Date    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
aide_os/
│
├── backend/                          # FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                 # Environment & settings
│   │   ├── schemas.py                # Pydantic request/response models
│   │   ├── main.py                   # API endpoints (all 7 routes)
│   │   └── engines/
│   │       ├── __init__.py
│   │       ├── url_engine.py         # Module 6: URL Score calculator
│   │       ├── chipflation_engine.py # Module 2: Decision Index
│   │       ├── emi_engine.py         # Module 7: Hidden fee extractor
│   │       └── recommendation_engine.py # Modules 3 & 4: Product matching
│   ├── tests/
│   │   └── test_engines.py           # 67 comprehensive pytest tests
│   ├── .env.example                  # Environment variable template
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                         # React Application (Vite)
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js             # Axios API client
│   │   ├── components/
│   │   │   └── Layout.jsx            # Sidebar & navigation shell
│   │   ├── hooks/
│   │   │   └── useApi.js             # Generic async API hook
│   │   ├── pages/
│   │   │   ├── HomePage.jsx          # Dashboard, chipflation snapshot, sale calendar
│   │   │   ├── DiagnosePage.jsx      # Device diagnosis form & URL results
│   │   │   ├── RecommendPage.jsx     # Product recommender & alternative cards
│   │   │   ├── EMIAuditPage.jsx      # EMI hidden charge auditor
│   │   │   └── ChipflationPage.jsx   # DI calculator & spot-market table
│   │   ├── App.jsx                   # Router & page wiring
│   │   ├── index.jsx                 # React root mount
│   │   └── index.css                 # Global design tokens & component styles
│   ├── .env.example                  # Frontend environment template
│   ├── index.html                    # Vite HTML entry point
│   ├── vite.config.js                # Vite + proxy config
│   └── package.json
│
├── bot/                              # Telegram Bot
│   ├── telegram_bot.py               # Price-drop notifications & deal alerts
│   └── requirements.txt
│
├── extension/                        # Chrome Extension
│   ├── manifest.json                 # Manifest V3 config
│   ├── icons/                        # Extension icons
│   └── *.js / *.html                 # Inline price-check UI
│
├── infra/
│   └── schema.sql                    # PostgreSQL DDL + 100-product seed data
│
├── docker-compose.yml                # Full-stack orchestration
├── .gitignore
└── README.md
```

---

## 🚀 Zero-Cost Deployment (₹0 Investment)

Deploy the entire stack for **zero cost** using free tiers of **SnapDeploy**, Vercel, Neon, and Upstash. **No credit card required** — ever.

### Deployment Architecture

```
┌──────────────────────┐     ┌─────────────────────────────┐
│   Vercel (Free)      │────▶│  SnapDeploy (Free)          │
│   React Frontend     │     │  FastAPI Backend + Bot      │
│   Auto-deploy on     │     │  2 containers, 100 hrs      │
│   every push         │     │  Auto-sleep/wake 10-30s     │
└──────────────────────┘     └─────────────┬───────────────┘
                                          │
                              ┌───────────┴───────────┐
                              │                       │
                    ┌─────────▼──────┐      ┌────────▼──────────┐
                    │  Neon (Free)   │      │  Upstash (Free)    │
                    │  PostgreSQL    │      │  Redis             │
                    │  0.5GB storage │      │  256MB / 500K cmds │
                    └────────────────┘      └────────────────────┘
```

---

### Step 1: Neon PostgreSQL (2 min)

1. Sign up at [neon.tech](https://neon.tech) — **no credit card required**
2. Click **Create Project** → choose a region close to your users
3. Copy the **connection string** (it ends with `?sslmode=require`)
4. Save this as `DATABASE_URL` — you'll need it later

> **Tip:** Neon's free tier gives you 0.5GB storage, enough for **10,000+ products**.

---

### Step 2: Upstash Redis (2 min)

1. Sign up at [upstash.com](https://upstash.com) — **no credit card required**
2. Click **Create Database** → choose **Redis** → pick the closest region
3. Copy the **REDIS_URL** from the database details page

> **Tip:** Free tier includes 256MB storage and 500K commands/month — more than enough for rate limiting and caching.

---

### Step 3: GitHub Repository (1 min)

1. Ensure code is pushed to GitHub (already done: [github.com/AiWujie/aide_os](https://github.com/AiWujie/aide_os))
2. Make sure the repository is **public** (required for SnapDeploy free tier)

---

### Step 4: SnapDeploy Backend + Bot (5 min)

1. Sign up at [snapdeploy.dev](https://snapdeploy.dev) — **no credit card required**
2. Click **New Container** → **Connect GitHub** → select `aide_os` repo
3. **Deploy Backend** (FastAPI):
   - Container name: `aide-os-api` (becomes `aide-os-api.containers.snapdeploy.app`)
   - Root directory: `backend`
   - Uses `backend/Dockerfile` (already included)
   - Port: `8000`
   - Health check path: `/api/v1/health`
   - Environment variables (add in dashboard):
     - `DATABASE_URL` — from Step 1
     - `REDIS_URL` — from Step 2
     - `SECRET_KEY` — generate: `python -c "import secrets; print(secrets.token_hex(32))"`
     - `DEBUG` = `false`
     - `ENVIRONMENT` = `production`
     - `CORS_ORIGINS` = `["https://aide-os.vercel.app","http://localhost:3000"]`
4. **Deploy Bot** (Telegram):
   - Click **New Container** → same repo
   - Container name: `aide-os-bot`
   - Root directory: `bot`
   - Uses `bot/Dockerfile` (already included)
   - No port needed (background worker)
   - Environment variables:
     - `DATABASE_URL` — from Step 1
     - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
     - `BOT_CHAT_ID` — your Telegram chat ID
5. Click **Deploy** — builds in ~2-3 minutes

> **Verify:** Visit `https://aide-os-api.containers.snapdeploy.app/docs` to see the Swagger UI.

---

### Step 5: Vercel Frontend (3 min)

1. Sign up at [vercel.com](https://vercel.com) with your GitHub account
2. Click **Import** → select the `aide_os` repository
3. Configure:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

4. Add environment variable:
   - `VITE_API_URL` = `https://aide-os-api.containers.snapdeploy.app`

5. Click **Deploy** — builds in ~30 seconds

> **Bonus:** Vercel auto-deploys on every push to `main`. Custom domains are free.

---

### Step 6: Chrome Extension (optional, 10 min)

1. Open Chrome → navigate to `chrome://extensions`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked** → select the `extension/` folder from the repo
4. Test the extension on [Amazon.in](https://www.amazon.in) and [Flipkart.com](https://www.flipkart.com)
5. **To publish:** zip the `extension/` folder → submit to the [Chrome Web Store](https://chrome.google.com/webstore/devconsole) ($5 one-time fee)

---

### 🔑 Environment Variables

| Variable | Where to Set | Description |
|----------|-------------|-------------|
| `DATABASE_URL` | SnapDeploy Backend + Bot | PostgreSQL connection string from Neon |
| `REDIS_URL` | SnapDeploy Backend | Redis URL from Upstash |
| `SECRET_KEY` | SnapDeploy Backend | JWT/session secret — generate a random 64-char hex string |
| `TELEGRAM_BOT_TOKEN` | SnapDeploy Bot | Telegram Bot API token from @BotFather |
| `BOT_CHAT_ID` | SnapDeploy Bot | Target Telegram chat/group ID for notifications |
| `VITE_API_URL` | Vercel Frontend | Backend API URL (e.g. `https://aide-os-api.containers.snapdeploy.app`) |
| `DEBUG` | SnapDeploy Backend | Set to `false` for production |
| `ENVIRONMENT` | SnapDeploy Backend | Set to `production` |
| `CORS_ORIGINS` | SnapDeploy Backend | JSON array of allowed origins (Vercel URL + localhost) |

---

### ⚠️ Known Limitations

| Service | Free Tier Limit | Impact | Mitigation |
|---------|----------------|--------|------------|
| **SnapDeploy** | 2 containers, 100 hrs total runtime | Auto-sleeps after idle, 10-30s cold start | Auto-wakes on traffic; Always-On $12/mo if needed |
| **Neon** | 0.5GB storage, 100 compute-hours/mo | Enough for 10K+ products | Scale-to-zero saves compute hours |
| **Upstash** | 256MB, 500K commands/mo | Sufficient for rate limiting & caching | Monitor usage in dashboard |
| **Vercel** | Unlimited builds & bandwidth | Always-on, no cold starts | Best free tier of the stack |

> **Note:** SnapDeploy free tier hours never expire. Use at your own pace. For 24/7 uptime, Always-On starts at $12/mo per container.

---

### One-Click Deploy

| Service | Button |
|---------|--------|
| **Frontend** (Vercel) | [![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new) |
| **Backend** (SnapDeploy) | [![Deploy to SnapDeploy](https://snapdeploy.dev/button.svg)](https://snapdeploy.dev/new) |

---

## 🔌 API Reference

Base URL (deployed): `https://aide-os-api.onrender.com`

| Method | Endpoint | Module | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/v1/health` | — | Service health + version |
| `GET` | `/api/v1/categories` | — | Supported categories & use-cases |
| `POST` | `/api/v1/device-longevity` | 6 | URL score, years remaining, maintenance advice |
| `POST` | `/api/v1/chipflation-index` | 2 | Decision Index, market status, seasonal buy hint |
| `POST` | `/api/v1/emi-audit` | 7 | True cost, hidden charge breakdown, verdict |
| `POST` | `/api/v1/recommend` | 3 & 4 | Ranked products, alternatives, refurbished options |
| `POST` | `/api/v1/full-decision` | All | Combined single-call master decision engine |
| `GET` | `/api/v1/admin/chipflation/latest` | Admin | Latest chipflation data per component |
| `POST` | `/api/v1/admin/chipflation/update` | Admin | Insert new chipflation data point |

Full interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

### Example — Full Decision Request

```bash
curl -X POST https://aide-os-api.onrender.com/api/v1/full-decision \
  -H "Content-Type: application/json" \
  -d '{
    "current_category": "mobile",
    "current_age_months": 42,
    "current_battery_health_pct": 72,
    "current_storage_health_pct": 85,
    "current_physical_condition": 0.85,
    "target_use_case": "gaming",
    "max_budget_inr": 35000,
    "target_current_price": 32000,
    "target_historical_baseline": 27000,
    "emi_tenure_months": 6,
    "bank_processing_fee": 299,
    "forgone_cash_discount": 1500,
    "no_cost_discount": 2000
  }'
```

**Response summary:**

```json
{
  "master_verdict": "HOLD_CURRENT_DEVICE",
  "device_longevity": { "url_score_pct": 66.7, "estimated_years_left": 3.3 },
  "market_analysis":  { "decision_index": 1.066, "market_status": "INFLATED" },
  "emi_audit":        { "total_hidden_charges": 2212.82, "recommendation": "PAY_UPFRONT_CASH" }
}
```

---

## 🧪 Test Results

**67 tests across 4 engine modules — all passing ✅**

```bash
cd backend && python -m pytest tests/ -v
```

| Module | Test Class | Tests | Coverage |
|--------|-----------|-------|----------|
| 🔋 URL Engine | `TestURLEngine` | 14 | Normal, boundary, clamping, all 6 categories, edge cases |
| 📈 Chipflation Engine | `TestChipflationEngine` | 11 | Optimal, overpriced, moderate, urgency, all categories |
| 💳 EMI Audit Engine | `TestEMIEngine` | 11 | Pay-upfront, acceptable, reconsider, breakdowns, GST |
| 🎯 Recommendation Engine | `TestRecommendationEngine` | 14 | Budget, refurbished, filters, multi-category, value verdicts |
| 🔗 Integration | `TestFullDecision` | 17 | End-to-end `/full-decision` with varied inputs |

**Test categories covered:**
- ✅ Normal flows (happy path)
- ✅ Boundary conditions (exact 60.0 / 40.0 URL scores)
- ✅ Edge cases (brand-new devices, dead devices, zero inputs)
- ✅ Input clamping (out-of-range physical_condition, battery > 100%)
- ✅ Category parameterization (all 6 categories × each engine)
- ✅ Unknown/fallback category handling
- ✅ End-to-end integration (full-decision endpoint)

---

## 📊 Module Scoring

Each engine module has been validated with weighted scoring criteria:

| Module | Weight | Score | Criteria |
|--------|--------|-------|----------|
| **URL Engine** (Module 6) | 25% | ✅ 100/100 | 14 tests, 6 categories, boundary clamping verified |
| **Chipflation Engine** (Module 2) | 25% | ✅ 100/100 | 11 tests, 3 market states, urgency factor validated |
| **Recommendation Engine** (Modules 3 & 4) | 25% | ✅ 100/100 | 14 tests, budget filters, refurbished matching, value verdicts |
| **EMI Audit Engine** (Module 7) | 25% | ✅ 100/100 | 11 tests, 3 decision tiers, GST calculation at 18% |
| **Overall** | — | **✅ 100/100** | **67 tests, 4 engines, 0 failures** |

---

## 🛠 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite 6 | Multi-page SPA with hot reload |
| **Routing** | React Router v6 | Client-side page navigation |
| **HTTP Client** | Axios | API calls with interceptors |
| **Backend** | Python 3.11 + FastAPI | Async REST API engine |
| **Validation** | Pydantic v2 | Request / response schema validation |
| **Server** | Uvicorn | ASGI production server |
| **Database** | PostgreSQL 16 (Neon) | Gadget catalogue + financial meta |
| **Cache** | Redis 7 (Upstash) | Live price caching + rate limiting |
| **Containers** | Docker + Compose | One-command full-stack deployment |
| **Hosting** | Render (Backend) + Vercel (Frontend) | Zero-cost cloud deployment |
| **Notifications** | Telegram Bot (Render Worker) | Price-drop alerts & deal notifications |
| **Browser** | Chrome Extension (Manifest V3) | Inline price checking on e-commerce sites |

---

## 📱 Supported Categories

| Category | Use Cases | Chipflation Risk |
|----------|-----------|-----------------|
| 📱 **Mobile** | Gaming · Daily Tasks · Multitasking · Photography | 🔴 HIGH — LPDDR5X +18.5% YoY |
| 💻 **Laptop** | Coding · Data Science · Video Editing · Productivity | 🔴 HIGH — DDR5 +22.1% YoY |
| 🎧 **Audio** | ANC · Music · Remote Work · Travel | 🟢 LOW — BT SoC stable |
| 📺 **Video** | Gaming · Streaming · Home Theater | 🟡 LOW-MED — Panel yields stable |
| 💾 **Memory** | Fast Storage · Video Editing · Gaming | 🔴 HIGH — 3D NAND +24.3% YoY |
| ⌚ **Wearable** | Fitness · Health Tracking · Daily Use | 🟢 LOW — micro-AMOLED stable |

---

## 💼 Business Model

| Stream | Description |
|--------|-------------|
| **Affiliate Commissions** | Referral revenue on product purchases and certified refurbished conversions |
| **FinTech Lead Gen** | Revenue-share with banks and NBFCs on EMI and card-offer referrals |
| **Freemium Subscription** | Free basic tracking; Premium for real-time alerts and deal-sniping bots |
| **B2B Data Analytics** | Anonymised consumer purchasing sentiment sold to hardware manufacturers |

---

## 🌐 Live Demo

**Frontend:** https://omni-gadget.vercel.app/

**Backend API:** https://omni-gadget.onrender.com/

**Swagger Docs:** https://omni-gadget.onrender.com/docs

**Telegram Bot:** Check Render Background Worker logs (URL not exposed)

---

## 🤝 Contributing

Contributions welcome! Here's how to get started:

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/aide_os.git
   cd aide_os
   ```
3. **Set up** for local development:
   ```bash
   # Backend
   cd backend
   python -m venv .venv
   source .venv/Scripts/activate  # Windows
   # source .venv/bin/activate    # macOS / Linux
   pip install -r requirements.txt
   cp .env.example .env

   # Frontend
   cd ../frontend
   npm install
   cp .env.example .env.local
   ```
4. **Run tests** to verify everything works:
   ```bash
   cd backend && python -m pytest tests/ -v
   ```
5. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
6. **Commit** with clear messages, **push**, and open a **Pull Request**

### Contribution Guidelines

- Write tests for new engine logic (maintain the 100% pass rate)
- Follow the existing code style (Black for Python, Prettier for JS)
- Keep engines modular — each module should be independently testable
- Update the README if adding new features or deployment steps

---

## 🗺 What's Next

Remaining roadmap items to tackle:

- [ ] **Live e-commerce price scraper** — Real-time price monitoring from Amazon.in and Flipkart.com
- [ ] **TrendForce / DRAMeXchange API integration** — Live chipflation index from industry data sources
- [ ] **Community deal-verification crowdsource API** — User-submitted deal verification and voting
- [ ] **Mobile app (React Native)** — Native iOS/Android experience with push notifications
- [ ] **Batch price comparison tool** — Compare prices across 10+ e-commerce platforms simultaneously
- [ ] **ML price prediction model** — Forecast future price movements using historical chipflation data
- [ ] **Multi-language support** — Hindi, Tamil, Telugu, and other Indian regional languages
- [ ] **API rate limiting dashboard** — Usage monitoring and abuse prevention for public API consumers

### Recently Completed ✅

- [x] Telegram price-drop notification bot
- [x] Chrome Extension (Manifest V3) for inline price checking
- [x] DB-backed product catalogue (100+ products across 6 categories)
- [x] Device telemetry + EMI audit logging
- [x] Affiliate buy buttons (Amazon/Flipkart/EarnKaro)
- [x] 67 comprehensive tests across all 4 engines
- [x] Zero-cost cloud deployment (Render + Vercel + Neon + Upstash)
- [x] PWA support for mobile web install

---

## 📄 License

MIT — Open source, free to use, fork, and extend.

---

<div align="center">
  <sub>Built to fight planned obsolescence and provide full consumer financial transparency.</sub><br/>
  <sub><em>Always check the Chipflation Index before upgrading your hardware.</em></sub>
</div>
