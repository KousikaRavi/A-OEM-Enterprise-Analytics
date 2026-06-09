# A-OEM Enterprise Analytics Ecosystem
### Warranty Fraud & Leakage Detection | Data Analytics Portfolio Project

---

## The Business Problem

Warranty fraud and leakage cost industrial OEMs an estimated **1–3% of annual revenue** — often invisible until patterns are analysed at scale. In a dealer network spanning hundreds of service branches, individual fraudulent claims look routine. The signal only emerges in the data.

This project builds the analytics infrastructure to find it.

**What this project answers:**
- Which dealers are filing claims after warranty expiry?
- Are the same vehicles being claimed multiple times within short windows?
- Which service branches have abnormally high labour or parts costs?
- Are there vehicles being claimed before they were ever shipped to a retailer?
- Which dealers carry the highest composite fraud risk — and by how much?

---

## What I Built

A simulated end-to-end analytics environment modelled on real industrial OEM operations — grounded in 4+ years of implementing Toyota Material Handling's Dealer Management System on SAP SD/CRM.

| Layer | What it does |
|---|---|
| **3 source databases** | Separate ERP, CRM, and flat-file sources — mirrors real heterogeneous enterprise architecture |
| **Star schema warehouse** | Kimball-style dimensional model purpose-built for warranty claim analysis |
| **ETL pipeline** | Python scripts that clean, validate, and load data from all three sources |
| **Mock CRM REST API** | FastAPI layer simulating how real CRM systems (Salesforce, SAP CRM) expose data |
| **3,000 synthetic claims** | Faker-generated warranty claims with five deliberately planted fraud patterns |
| **5 diagnostic SQL queries** | Window functions, Z-scores, and composite risk scoring to surface fraud |
| **Power BI dashboard** | Four-visual fraud detection Command Center with KPI cards and slicers |

---

## Analytical Findings

### Fraud Patterns Planted & Detected

| Fraud Pattern | Volume Planted | Detection Method |
|---|---|---|
| Claims filed after warranty expiry | 5% of claims | `claim_date > warranty_expiry_date` join |
| Duplicate claims — same vehicle, <30 days | 3% of claims | Window function `LAG()` / `LEAD()` |
| Ghost vehicle IDs — vehicle never registered | 2% of claims | `LEFT JOIN dim_vehicle IS NULL` |
| Labour/parts cost outliers | 4% of claims | Z-score (`> 2 STDDEV` from dealer mean) |
| Claims before retail shipment date | 2% of claims | `claim_date < retail_shipment_date` |

All five patterns are detectable in SQL and surfaced visually in Power BI.

### Diagnostic SQL Queries

Each query in `sql_diagnostics/` targets a specific fraud vector:

**`fraud_01_expired_warranty.sql`**
Joins claim dates against warranty expiry dates. Groups by dealer to rank branches by expired-claim volume.

**`fraud_02_duplicate_claims.sql`**
Uses `LAG()` window function partitioned by `vehicle_id` ordered by `claim_date`. Flags any claim within 30 days of the previous claim on the same vehicle.

**`fraud_03_cost_outliers.sql`**
Calculates per-dealer mean and standard deviation for labour cost, parts cost, and travel cost. Flags claims where any cost component exceeds 2 standard deviations — surfaces inflated billing patterns.

**`fraud_04_dealer_risk_score.sql`**
Composite fraud risk score per dealer — weighted sum of all five fraud flags normalised against claim volume. Ranks dealers from highest to lowest risk. The key output for the Power BI heatmap.

**`fraud_05_early_claims.sql`**
Detects claims submitted before the vehicle's retail shipment date — logically impossible in a legitimate warranty workflow. Direct indicator of either data manipulation or ghost vehicle fraud.

### Power BI Dashboard — Fraud Detection Command Center

Four visuals connected to `aoem_warehouse`:

- **Filled Map** — Dealer fraud risk heatmap by Indian state (driven by `fraud_04` composite score)
- **Line Chart** — Monthly warranty claim trend 2022–2026, with fraud-flagged claims overlaid
- **Scatter Plot** — Cost anomaly visualisation: labour vs parts cost coloured by outlier flag
- **Matrix Table** — All five fraud flags broken down by dealer, sortable by risk score

**KPI Cards:** Total Claims | Fraud Flagged | Fraud % | Total Approved Amount

**Slicers:** Region / State | Date Range | Claim Status

---

## Data Quality — What the ETL Had to Handle

Real ETL is never clean. The source data deliberately includes production-grade data quality issues:

### crm_customer (969 rows)
| Issue | Volume | Handling |
|---|---|---|
| Inconsistent state names (e.g. "tamil nadu" vs "Tamil Nadu") | ~190 rows (20%) | `LOWER()` + `TRIM()` normalisation |
| Mixed date formats (DD/MM/YYYY, YYYY-MM-DD, epoch) | ~237 rows (25%) | `dateutil` flexible parser |
| Multiple phone number formats | All rows | Regex standardisation |
| Missing phone / email | ~142 rows (15%) | NULL handling strategy |
| Duplicate customer records | 19 rows (2%) | Deduplication on composite key |

### crm_vehicle (800 rows)
| Issue | Volume | Handling |
|---|---|---|
| Invalid dealer IDs (FK violations) | ~40 rows (5%) | Soft FK validation — log and quarantine |
| Orphan customer IDs | ~24 rows (3%) | Referential integrity check pre-load |
| Future `date_of_first_use` | ~16 rows (2%) | Business rule validation |

---

## Architecture

```
SOURCE LAYER                    ETL LAYER              WAREHOUSE LAYER
────────────────                ─────────              ───────────────────
CSV (dim_geo.csv)    ──────→   etl_geo.py    ──────→  dim_region
                                                        dim_state
                                                        dim_district

erp_db (PostgreSQL)  ──────→   etl_dealer.py ──────→  dim_dealer
└── erp_dealer

crm_db (PostgreSQL)  ──────→   etl_customer.py ────→  dim_customer
exposed via                     etl_vehicle.py  ────→  dim_vehicle
FastAPI REST API

Python Simulation    ──────→   simulate_claims.py ──→  fact_warranty_claim
(fraud anomalies)               (5 fraud patterns)

                                                        dim_date
                                                              ↓
                                                        Power BI
                                                        Fraud Detection
                                                        Dashboard
```

### Why three separate source databases?
Simulates real enterprise heterogeneous sources. Each requires a different ingestion pattern — flat file, direct DB, and REST API. The ETL logic for each is genuinely different.

### Why FastAPI instead of direct DB access for CRM?
Production CRM systems expose APIs, not raw DB connections. FastAPI simulates that boundary — the same ETL code works whether the URL points to localhost or a live Salesforce endpoint.

### Why surrogate keys in the warehouse?
Source system business keys can change format or be reused. Surrogate keys decouple warehouse history from source system changes — standard Kimball dimensional modelling practice.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Warehouse | PostgreSQL (`aoem_warehouse`) |
| Source ERP | PostgreSQL (`erp_db`) |
| Source CRM | PostgreSQL (`crm_db`) |
| REST API | FastAPI + Uvicorn |
| ETL | Python, Pandas, SQLAlchemy |
| Synthetic Data | Faker |
| Configuration | python-dotenv |
| Logging | Python logging module |
| Visualization | Power BI Desktop |
| Version Control | Git + GitHub |

---

## Project Structure

```
Project_AOEM/
├── config.py                    ← Centralised DB connections (SQLAlchemy)
├── .env                         ← Credentials (git ignored)
├── .env.example                 ← Template for contributors
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── dim_geo.csv              ← Indian geography source
│   └── dealer_hierarchy.csv    ← Dealer master data
│
├── etl_scripts/
│   ├── etl_geo.py                ← CSV → dim_region/state/district
│   ├── etl_dealer.py             ← erp_db → dim_dealer
│   ├── etl_customer.py           ← CRM API → dim_customer
│   ├── etl_vehicle.py            ← CRM API → dim_vehicle
│   └── generate_crm_data.py      ← Synthetic CRM data with quality issues
│
├── crm_api/
│   └── app.py                    ← FastAPI mock CRM API
│
├── simulation/
│   └── simulate_claims.py      ← Fraud simulation (3,000 claims)
│
└── sql_diagnostics/
    ├── fraud_01_expired_warranty.sql
    ├── fraud_02_duplicate_claims.sql
    ├── fraud_03_cost_outliers.sql
    ├── fraud_04_dealer_risk_score.sql
    └── fraud_05_early_claims.sql
```

---

## Setup

### Prerequisites
- Python 3.12+ · PostgreSQL 14+ · Power BI Desktop

```bash
# 1. Clone
# 1. Clone
git clone https://github.com/KousikaRavi/A-OEM-Enterprise-Analytics.git
cd A-OEM-Enterprise-Analytics

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate          # Windows

# 3. Dependencies
pip install -r requirements.txt

# 4. Configure credentials
cp .env.example .env
# Edit .env with your PostgreSQL credentials and API key

# 5. Create databases
# In psql:
CREATE DATABASE aoem_warehouse ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE erp_db         ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE crm_db         ENCODING 'UTF8' TEMPLATE template0;

# 6. Run ETL pipeline in order
python etl_scripts/etl_geo.py
python etl_scripts/etl_dealer.py
python etl_scripts/generate_crm_data.py

# 7. Start CRM API
uvicorn crm_api.app:app --reload --port 8000
# Swagger docs → http://localhost:8000/docs

# 8. Load CRM dimensions
python etl_scripts/etl_customer.py
python etl_scripts/etl_vehicle.py

# 9. Run fraud simulation
python simulation/simulate_claims.py

# 10. Open Power BI — connect to aoem_warehouse
```

---

## Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | PostgreSQL schema — 3 databases, star schema | ✅ Complete |
| Phase 2 | Synthetic data generation + planted anomalies | ✅ Complete |
| Phase 3 | FastAPI mock CRM API | ✅ Complete |
| Phase 4 | Python ETL pipeline | 🔄 In Progress |
| Phase 5 | Fraud simulation — 3,000 warranty claims | ⏳ Upcoming |
| Phase 6 | Diagnostic SQL — 5 fraud detection queries | ⏳ Upcoming |
| Phase 7 | Power BI fraud detection dashboard | ⏳ Upcoming |

---

## Portfolio Context

| # | Project | Stack | Status |
|---|---|---|---|
| MBA | Stock Clustering for Sector Analysis | Python · K-Means · PCA | ✅ Complete |
| 01 | Retail Sales Dashboard | Excel | ✅ Complete |
| 02 | ShopSphere Sales Analytics | MySQL · Power BI | ✅ Complete |
| 03 | **A-OEM Enterprise Analytics** ← You are here | PostgreSQL · Python · Power BI | 🔄 In Progress |

---

## Domain Background

Schema design and business logic are grounded in 4+ years implementing Toyota Material Handling's Dealer Management System on SAP SD/CRM at Infosys — specifically dealer hierarchy topology, vehicle registration workflows, and warranty claim processing structures.

*Dataset is fully synthetic. No real Toyota, Infosys, or dealer data is used. All business scenarios are simulated for portfolio purposes.*

---

## Author

**Kousika Ravi** — Data Analyst | Business Analyst | SAP Functional Consultant (SD/CRM) | MBA Business Analytics

📍 Tamil Nadu, India
🔗 [LinkedIn](https://linkedin.com/in/kousika-ravi) | [Portfolio](https://kousikaravi.github.io) | [GitHub](https://github.com/KousikaRavi)