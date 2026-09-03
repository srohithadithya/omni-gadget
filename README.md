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

> **Beat chipflation. Know when to buy, when to hold, and what your "No-Cost EMI" actually costs.**

</div>

---

## 📋 Table of Contents

1. [Problem Statement](#-problem-statement)
2. [Core Engine Modules](#-core-engine-modules)
3. [Mathematical Formulations](#-mathematical-formulations)
4. [System Architecture](#-system-architecture)
5. [Project Structure](#-project-structure)
6. [Getting Started](#-getting-started)
7. [API Reference](#-api-reference)
8. [Technology Stack](#-technology-stack)
9. [Supported Categories](#-supported-categories)
10. [Business Model](#-business-model)
11. [Roadmap](#-roadmap)

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
├── infra/
│   └── schema.sql                    # PostgreSQL DDL + 20-product seed data
│
├── docker-compose.yml                # Full-stack orchestration
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Docker + Docker Compose | v24+ |
| Node.js *(local dev only)* | v20+ |
| Python *(local dev only)* | v3.11+ |

---

### Option A — Docker Compose *(Recommended)*

Spins up PostgreSQL, Redis, the FastAPI backend, and the React frontend in one command.

```bash
git clone <your-repo-url> aide_os
cd aide_os
docker-compose up -d --build
```

| Service | URL |
|---------|-----|
| React Dashboard | http://localhost:3000 |
| FastAPI + Swagger | http://localhost:8000/docs |
| PostgreSQL | `localhost:5432` · db: `aideosdb` |
| Redis | `localhost:6379` |

---

### Option B — Local Development *(Hot Reload)*

**1. Backend**

```bash
cd backend
cp .env.example .env          # edit if needed
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**2. Frontend** *(new terminal)*

```bash
cd frontend
cp .env.example .env.local    # edit if needed
npm install
npm run dev
```

| Service | URL |
|---------|-----|
| React Dashboard | http://localhost:3000 |
| FastAPI + Swagger | http://localhost:8000/docs |

---

## 🔌 API Reference

Base URL (local dev): `http://localhost:8001`

| Method | Endpoint | Module | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/v1/health` | — | Service health + version |
| `GET` | `/api/v1/categories` | — | Supported categories & use-cases |
| `POST` | `/api/v1/device-longevity` | 6 | URL score, years remaining, maintenance advice |
| `POST` | `/api/v1/chipflation-index` | 2 | Decision Index, market status, seasonal buy hint |
| `POST` | `/api/v1/emi-audit` | 7 | True cost, hidden charge breakdown, verdict |
| `POST` | `/api/v1/recommend` | 3 & 4 | Ranked products, alternatives, refurbished options |
| `POST` | `/api/v1/full-decision` | All | Combined single-call master decision engine |

Full interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

### Example — Full Decision Request

```bash
curl -X POST http://localhost:8001/api/v1/full-decision \
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

## 🛠 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite 6 | Multi-page SPA with hot reload |
| **Routing** | React Router v6 | Client-side page navigation |
| **HTTP Client** | Axios | API calls with interceptors |
| **Backend** | Python 3.11 + FastAPI | Async REST API engine |
| **Validation** | Pydantic v2 | Request / response schema validation |
| **Server** | Uvicorn | ASGI production server |
| **Database** | PostgreSQL 16 | Gadget catalogue + financial meta |
| **Cache** | Redis 7 | Live price caching + rate limiting |
| **Containers** | Docker + Compose | One-command full-stack deployment |

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

## 🗺 Roadmap

- [x] URL Score engine (Module 6)
- [x] Chipflation Decision Index (Module 2)
- [x] Product recommender + refurbished matcher (Modules 3 & 4)
- [x] True-cost EMI auditor (Module 7)
- [x] Full-decision master endpoint
- [x] React multi-page frontend
- [x] PostgreSQL schema + seed data
- [x] Docker Compose stack
- [ ] Live e-commerce price scraper (Amazon / Flipkart)
- [ ] TrendForce / DRAMeXchange API integration for real-time chipflation index
- [ ] Telegram / WhatsApp price-drop notification bot
- [ ] Community deal-verification crowdsource API
- [ ] Mobile app (React Native)
- [ ] Browser extension (Manifest V3) for inline price checking

---

## 📄 License

MIT — Open source, free to use, fork, and extend.

---

<div align="center">
  <sub>Built to fight planned obsolescence and provide full consumer financial transparency.</sub><br/>
  <sub><em>Always check the Chipflation Index before upgrading your hardware.</em></sub>
</div>
