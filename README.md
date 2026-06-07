# A-OEM Enterprise Analytics Ecosystem
### Warranty Fraud & Leakage Detection | Data Analytics Portfolio Project

---

## The Business Problem

**Warranty fraud and leakage cost OEMs 1–3% of annual revenue.**

In automotive and industrial equipment distribution, warranty claims flow through dealer networks where fraud is hard to detect — duplicate submissions, inflated costs, expired warranty claims, and ghost vehicles all drain revenue silently.

This project builds the analytics infrastructure to **detect, quantify, and visualise** warranty fraud across a simulated Indian dealer network — answering the questions a business analyst would actually be asked:

- Which dealers have the highest fraud risk?
- What % of claims are filed after warranty expiry?
- Where are cost outliers concentrated — by region, dealer, or component?
- How much approved amount is at risk from duplicate claims?

---

## What This Project Delivers

### 5 Fraud Detection SQL Queries
Each query targets a specific fraud pattern and is designed to be run directly against the warehouse for business reporting:

| Query | Fraud Pattern | Business Impact |
|---|---|---|
| `fraud_01_expired_warranty.sql` | Claims filed after warranty expiry | Direct financial leakage |
| `fraud_02_duplicate_claims.sql` | Same vehicle, claims within 30 days | Double payment risk |
| `fraud_03_cost_outliers.sql` | Labor/parts cost > 2 STDDEV from mean | Inflated claim amounts |
| `fraud_04_dealer_risk_score.sql` | Composite fraud risk score per dealer | Dealer audit prioritisation |
| `fraud_05_early_claims.sql` | Claims before vehicle retail shipment | Ghost vehicle / data fraud |

### Power BI Fraud Detection Dashboard
Four visuals built on `aoem_warehouse` showing:
- **Filled Map** — Dealer fraud risk heatmap by state
- **Line Chart** — Monthly warranty claim trend (2022–2026)
- **Scatter Plot** — Cost anomaly visualisation
- **Matrix Table** — Fraud flags breakdown by dealer

**KPI Cards:** Total Claims | Fraud Flagged | Fraud % | Total Approved at Risk

**Slicers:** Region / State | Date Range | Claim Status

### Fraud Findings (Simulated Dataset — 3,000 Claims)

| Fraud Pattern | Volume | Approved Amount at Risk |
|---|---|---|
| Expired warranty claims | 5% (~150 claims) | Quantified per dealer |
| Duplicate submissions | 3% (~90 claims) | Double payment exposure |
| Ghost vehicle IDs | 2% (~60 claims) | Full claim value at risk |
| Cost outliers (labor/parts) | 4% (~120 claims) | Excess above mean |
| Early claims (pre-shipment) | 2% (~60 claims) | Process control failure |

---

## Domain Background

Schema design, KPI logic, and fraud pattern selection are grounded in **4+ years of experience on Toyota Material Handling's Dealer Management System** at Infosys — specifically:

- Dealer hierarchy topology (Main + Branch structure)
- Vehicle registration and warranty activation workflows
- Warranty claim processing and rejection rules
- SAP SD / CRM / ECC data flows from Opportunity to Warranty Claim

The business logic reflects how warranty data actually behaves in production dealer networks.

---

## How the Data Was Built

To analyse warranty fraud, you need warranty data — including fraudulent claims. Since real data can't be used, this project generates a realistic synthetic dataset with **deliberately planted fraud patterns**:

### Source Data
| Source | Records | Notes |
|---|---|---|
| `erp_db` | 798 dealers | Main + Branch hierarchy across Indian states |
| `crm_db` | 969 customers, 800 vehicles | B2B/B2C mix with planted data quality issues |
| `dim_geo.csv` | Indian geography | Region → State → District hierarchy |

### Planted Data Quality Issues (for realistic ETL)
| Issue | Volume | Why it matters |
|---|---|---|
| Inconsistent state names | ~190 rows (20%) | Real CRM data is always dirty |
| Mixed date formats | ~237 rows (25%) | Common in multi-system environments |
| Duplicate customers | 19 rows (2%) | Tests deduplication logic |
| Invalid dealer IDs | ~40 rows (5%) | Tests referential integrity |
| Orphan customer records | ~24 rows (3%) | Tests FK validation |

### Warehouse — Star Schema
```
dim_dealer ──────────────────────────────────────┐
dim_customer ────────────────────────────────┐   │
dim_vehicle ─────────────────────────────┐   │   │
dim_date ────────────────────────────┐   │   │   │
dim_region / dim_state / dim_district│   │   │   │
                                     ↓   ↓   ↓   ↓
                                fact_warranty_claim
                                ├── labor_cost
                                ├── parts_cost
                                ├── travel_cost
                                ├── total_claimed
                                ├── total_approved
                                ├── is_expired_warranty
                                ├── is_duplicate_claim
                                ├── is_ghost_vehicle
                                ├── is_early_claim
                                └── is_cost_outlier
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Analytics** | SQL — Window Functions, Z-score, CTEs | Fraud detection queries |
| **Dashboard** | Power BI Desktop | Business reporting |
| **Warehouse** | PostgreSQL (aoem_warehouse) | Star schema — fact + dims |
| **ETL** | Python, Pandas, SQLAlchemy | Multi-source data pipeline |
| **Source ERP** | PostgreSQL (erp_db) | Dealer master data |
| **Source CRM** | PostgreSQL (crm_db) via FastAPI | Customer + vehicle data |
| **Data Generation** | Python, Faker | Synthetic claims with fraud |

---

## Project Structure

```
Project_AOEM/
│
├── sql_diagnostics/              ← FRAUD DETECTION QUERIES (core DA output)
│   ├── fraud_01_expired_warranty.sql
│   ├── fraud_02_duplicate_claims.sql
│   ├── fraud_03_cost_outliers.sql
│   ├── fraud_04_dealer_risk_score.sql
│   └── fraud_05_early_claims.sql
│
├── simulation/
│   └── simulate_claims.py        ← Generates 3,000 claims with fraud patterns
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
├── data/
│   ├── dim_geo.csv               ← Indian geography source
│   └── dealer_hierarchy.csv      ← Dealer master
│
├── config.py                     ← DB connections
├── .env.example                  ← Credential template
├── .gitignore
└── requirements.txt
```

---

## Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | PostgreSQL schema — 3 databases, star schema design | ✅ Complete |
| Phase 2 | Synthetic data generation — dealers, vehicles, customers | ✅ Complete |
| Phase 3 | FastAPI mock CRM API + ETL pipeline (geo, dealer) | ✅ Complete |
| Phase 4 | ETL — customer and vehicle dimensions | 🔄 In Progress |
| Phase 5 | Fraud simulation — 3,000 warranty claims with 5 fraud patterns | ⏳ Upcoming |
| Phase 6 | Diagnostic SQL — 5 fraud detection queries | ⏳ Upcoming |
| Phase 7 | Power BI fraud detection dashboard | ⏳ Upcoming |

---

## Setup Instructions

### Prerequisites
- Python 3.12+ · PostgreSQL 14+ · Power BI Desktop

### Quick Start
```bash
# 1. Clone
git clone https://github.com/KousikaRavi/A-OEM-Enterprise-Analytics.git
cd A-OEM-Enterprise-Analytics

# 2. Environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 3. Create databases (in psql)
CREATE DATABASE aoem_warehouse ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE erp_db         ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE crm_db         ENCODING 'UTF8' TEMPLATE template0;

# 4. Run ETL
python etl_scripts/etl_geo.py
python etl_scripts/etl_dealer.py
python etl_scripts/generate_crm_data.py

# 5. Start CRM API
uvicorn crm_api.app:app --reload --port 8000
# Swagger docs → http://localhost:8000/docs

# 6. Complete ETL
python etl_scripts/etl_customer.py
python etl_scripts/etl_vehicle.py

# 7. Run fraud simulation
python simulation/simulate_claims.py

# 8. Open Power BI → connect to aoem_warehouse
```

---

## Portfolio Context

| # | Project | Stack | Status |
|---|---|---|---|
| MBA | Stock Clustering for Sector Analysis | Python · K-Means · PCA | ✅ Complete |
| 01 | Retail Sales Dashboard | Excel | ✅ Complete |
| 02 | ShopSphere Sales Analytics | MySQL · Power BI | ✅ Complete |
| 03 | **A-OEM Enterprise Analytics** ← You are here | PostgreSQL · Python · Power BI | 🔄 In Progress |

---
## Author

**Kousika Ravi** — Business Analyst | Data Analyst | SAP Functional Consultant (SD/CRM) | MBA Business Analytics

📍 Tamil Nadu, India  
🔗 [LinkedIn](https://linkedin.com/in/kousika-ravi) | [Portfolio](https://kousikaravi.github.io) | [GitHub](https://github.com/KousikaRavi)


*Dataset is fully synthetic. No real Toyota, Infosys, or dealer data is used. All business scenarios are simulated for portfolio purposes.*
