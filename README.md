<div align="center">
  <h1>⚡ AIDE-OS</h1>
  <p><strong>AI-Driven Electronic Device Ecosystem — Dynamic Pricing & Decision Engine</strong></p>
  <p><i>v4.0.0-PROD</i></p>
</div>

<br />

## 📖 Context & Problem Statement: The "Chipflation" Phenomenon
The rapid expansion of enterprise AI infrastructure has disrupted the consumer semiconductor supply chain. Foundry leaders have reallocated manufacturing capacity toward high-margin enterprise AI chips and High-Bandwidth Memory (HBM). Consequently, consumer LPDDR5/DDR5 DRAM and 3D NAND flash face severe supply constraints. 

**AIDE-OS** solves this by evaluating real-time market inflation, assessing current hardware health, predicting pricing windows, and recommending optimal financial strategies to maximize consumer value.

---

## 🃏 Core Engine Modules (Flash Cards)

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🔋 1. Device Longevity (URL) Engine</h3>
      <p>Calculates <strong>Useful Remaining Life (URL)</strong> for current hardware based on battery wear, storage TBW, physical condition, and OS limits. Prevents premature upgrades.</p>
      <em>Output: Hold vs. Replace + Remaining Years</em>
    </td>
    <td width="50%" valign="top">
      <h3>📈 2. Chipflation Decision Index (DI)</h3>
      <p>Live spot-market component tracker. Factors upstream DRAM/NAND costs to determine if retail prices are artificially inflated.</p>
      <em>Output: OVERPRICED_HOLD / OPTIMAL_BUY</em>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🎯 3. Smart Recommender & Alt-Match</h3>
      <p>A spec-to-use-case filtering engine mapping user workloads (Coding, Gaming) to ideal devices. Connects to the certified refurbished market for cross-brand alternatives.</p>
      <em>Output: Primary & Refurbished Matches</em>
    </td>
    <td width="50%" valign="top">
      <h3>💳 4. EMI Hidden Fee Auditor</h3>
      <p>Exposes the true cost of "No-Cost EMI". Calculates bank processing fees, the 18% GST levied on interest components, and forgone instant UPI cash discounts.</p>
      <em>Output: True Effective Outlay</em>
    </td>
  </tr>
</table>

---

## 🏗 System Architecture

**AIDE-OS** relies on a modern, decoupled microservice stack designed for scalability.

*   **Frontend**: React.js 18 + Vite (Responsive multi-page dashboard)
*   **Backend API**: Python 3.12 + FastAPI (High-performance Async REST Engine)
*   **Database Engine**: PostgreSQL 16 (Gadget Catalog, Financial Meta, Chipflation Logs)
*   **Caching & Queue**: Redis 7 (Rate Limiting, Live Price Caching)
*   **Infrastructure**: Docker & Docker Compose (Complete containerized stack)

### 📂 Directory Structure

```text
aide_os/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── engines/          # Core mathematical logic (URL, DI, EMI, Recommender)
│   │   └── main.py           # REST endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React Application (Vite)
│   ├── src/
│   │   ├── api/              # Axios client mapping
│   │   ├── components/       # Layout & navigation
│   │   └── pages/            # Feature-specific interactive dashboards
│   ├── package.json
│   └── vite.config.js
├── infra/                    # Database & Initialization
│   └── schema.sql            # PostgreSQL DDL and master seed data
└── docker-compose.yml        # Full-stack orchestration
```

---

## 🚀 Getting Started

### Prerequisites
* Docker & Docker Compose
* Node.js v24+ (If running frontend locally outside Docker)
* Python 3.11+ (If running backend locally outside Docker)

### Option 1: Full Stack via Docker (Recommended)
1. Clone the repository and navigate to the root directory.
2. Run the deployment sequence:
   ```bash
   docker-compose up -d --build
   ```
3. **Access the Application**:
   * **Dashboard (React)**: http://localhost:3000
   * **API Swagger Docs**: http://localhost:8000/docs
   * **PostgreSQL DB**: `localhost:5432` (User: `aideuser` / Pass: `aidepass`)

### Option 2: Local Development Mode (Hot Reloading)

**1. Start the Backend API (Port 8001)**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Or venv/bin/activate on Mac/Linux
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**2. Start the Frontend App (Port 3000)**
```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 Core API Endpoints Reference

The FastAPI backend exposes the following centralized routes:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health status and uptime block. |
| `POST` | `/api/v1/device-longevity` | Computes hardware URL score and maintenance steps. |
| `POST` | `/api/v1/chipflation-index` | Calculates dynamic Buy-vs-Hold index against spot prices. |
| `POST` | `/api/v1/recommend` | Maps workload specs to target products & refurb tiers. |
| `POST` | `/api/v1/emi-audit` | Breaks down hidden GST and processing surcharges. |
| `POST` | `/api/v1/full-decision` | Master endpoint running all 4 engines in a single lifecycle. |

---

## 📄 License & Open-Source Tenets
Built as an open-source analytics engine. Designed to fight planned obsolescence and provide full consumer financial transparency. 

*Always check the live Chipflation Index before upgrading your hardware.*
