# A-OEM Enterprise Analytics Ecosystem
### Warranty Leakage & Fraud Detection | End-to-End Data Engineering Portfolio Project

---

## Overview

A-OEM Enterprise Analytics Ecosystem is a full-stack data engineering project simulating a real-world industrial OEM's analytics infrastructure. Built on domain experience from Toyota Material Handling's Dealer Management System, this project demonstrates multi-source ETL pipelines, a star schema data warehouse, a mock CRM REST API, synthetic data simulation with planted fraud anomalies, diagnostic SQL, and a Power BI fraud detection dashboard.

The core business problem: **Warranty fraud and leakage cost OEMs 1–3% of annual revenue.** This project builds the data infrastructure to detect it.

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
(Level 2)                       (with fraud anomalies)

                                                        dim_date
                                                        (generated)
                                                              ↓
                                                        Power BI
                                                        Fraud Detection
                                                        Dashboard
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Warehouse | PostgreSQL (aoem_warehouse) |
| Source ERP | PostgreSQL (erp_db) |
| Source CRM | PostgreSQL (crm_db) |
| REST API | FastAPI + Uvicorn |
| ETL | Python, Pandas, SQLAlchemy |
| Synthetic Data | Faker |
| Configuration | python-dotenv |
| Logging | Python logging module |
| Visualization | Power BI Desktop |
| Version Control | Git + GitHub |

---

## Database Design

### Source Systems

**erp_db** — Simulates an internal ERP system
- `erp_dealer` — 798 dealers across Indian states (Main + Branch hierarchy)

**crm_db** — Simulates an external CRM system exposed via REST API
- `crm_customer` — 969 customers (B2B/B2C, with planted data quality issues)
- `crm_vehicle` — 800 forklift vehicles with warranty metadata

### Warehouse — Star Schema (aoem_warehouse)

```
dim_region
dim_state ──────────────────────────────────────────────┐
dim_district                                             │
dim_date ────────────────────────────────────────────┐  │
dim_dealer ──────────────────────────────────────┐   │  │
dim_customer ────────────────────────────────┐   │   │  │
dim_vehicle ─────────────────────────────┐   │   │   │  │
                                         ↓   ↓   ↓   ↓  ↓
                                    fact_warranty_claim
```

**fact_warranty_claim** columns include:
- Surrogate FKs to all dimensions
- Financial metrics: `labor_cost`, `parts_cost`, `travel_cost`, `total_claimed`, `total_approved`
- Fraud flags: `is_expired_warranty`, `is_duplicate_claim`, `is_ghost_vehicle`, `is_early_claim`, `is_cost_outlier`
- Audit fields: `days_to_settle`, `hour_meter_at_claim`, `claim_status`, `rejection_reason`

---

## Data Quality — Planted Issues

This project deliberately introduces real-world data quality problems to simulate genuine ETL challenges:

### crm_customer (969 rows)
| Issue | Volume | Purpose |
|---|---|---|
| Inconsistent state names | ~190 rows (20%) | Tests LOWER + TRIM normalization |
| Mixed date formats | ~237 rows (25%) | Tests dateutil parsing |
| Multiple phone formats | All rows | Tests regex standardization |
| Missing phone/email | ~142 rows (15%) | Tests NULL handling |
| Duplicate customers | 19 rows (2%) | Tests deduplication logic |

### crm_vehicle (800 rows)
| Issue | Volume | Purpose |
|---|---|---|
| Invalid dealer_ids | ~40 rows (5%) | Tests soft FK validation |
| Orphan customer_ids | ~24 rows (3%) | Tests referential integrity check |
| Future date_of_first_use | ~16 rows (2%) | Tests business rule validation |

---

## Mock CRM API (FastAPI)

The CRM data is exposed via an authenticated REST API — simulating how real enterprise CRM systems (Salesforce, SAP CRM) expose data to external ETL pipelines.

**Base URL:** `http://localhost:8000`

**Authentication:** `X-API-Key` header required on all endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | API health check |
| GET | `/api/customers?page=1&limit=100` | Paginated customer list |
| GET | `/api/customers/{customer_id}` | Single customer by ID |
| GET | `/api/vehicles?page=1&limit=100` | Paginated vehicle list |
| GET | `/api/vehicles/{vehicle_id}` | Single vehicle by ID |

**Interactive docs:** `http://localhost:8000/docs` (Swagger UI)

**Design decisions:**
- Pagination prevents memory overload on large datasets
- API key auth simulates real enterprise authentication boundaries
- Parameterized queries prevent SQL injection
- Structured logging on all endpoints for observability

---

## Fraud Anomalies — Level 2 Simulation

3,000 warranty claims generated (2022–2026) with deliberately planted fraud patterns:

| Fraud Pattern | Volume | Detection Method |
|---|---|---|
| Claim after warranty expiry | 5% | `claim_date > warranty_expiry_date` |
| Duplicate claims (same vehicle, <30 days) | 3% | Window function LAG/LEAD |
| Ghost vehicle IDs | 2% | LEFT JOIN dim_vehicle IS NULL |
| Labor cost outliers (>3x mean) | 4% | Z-score / STDDEV |
| Claim before retail shipment | 2% | `claim_date < retail_shipment_date` |

---

## Diagnostic SQL

Five fraud detection queries in `sql_diagnostics/`:

```
fraud_01_expired_warranty.sql   → Claims filed after warranty expiry by dealer
fraud_02_duplicate_claims.sql   → Same vehicle, claims within 30 days (window fn)
fraud_03_cost_outliers.sql      → Labor/parts cost > 2 STDDEV from mean
fraud_04_dealer_risk_score.sql  → Composite fraud risk score per dealer
fraud_05_early_claims.sql       → Claims before vehicle retail shipment date
```

---

## Power BI Dashboard

Four visuals connected to `aoem_warehouse` via Import mode:

- **Filled Map** — Dealer fraud risk heatmap by state
- **Line Chart** — Monthly warranty claim trend (2022–2026)
- **Scatter Plot** — Cost anomaly visualization
- **Matrix Table** — Fraud flags breakdown by dealer

KPI Cards: Total Claims | Fraud Flagged | Fraud % | Total Approved Amount

Slicers: Region / State | Date Range | Claim Status

---

## Project Structure

```
Project_AOEM/
├── config.py                    ← Centralized DB connections (SQLAlchemy)
├── .env                         ← Credentials (git ignored)
├── .env.example                 ← Template for contributors
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── dim_geo.csv              ← Indian geography (source for dim tables)
│   └── dealer_hierarchy.csv    ← Dealer master data
│
├── etl_scripts/
│   ├── generate_crm_data.py    ← Faker synthetic data generator
│   ├── etl_geo.py              ← CSV → dim_region/state/district
│   ├── etl_dealer.py           ← erp_db → dim_dealer
│   ├── etl_customer.py         ← CRM API → dim_customer
│   └── etl_vehicle.py          ← CRM API → dim_vehicle
│
├── crm_api/
│   ├── __init__.py
│   └── app.py                  ← FastAPI mock CRM REST API
│
├── simulation/
│   └── simulate_claims.py      ← Level 2 fraud simulation
│
└── sql_diagnostics/
    ├── fraud_01_expired_warranty.sql
    ├── fraud_02_duplicate_claims.sql
    ├── fraud_03_cost_outliers.sql
    ├── fraud_04_dealer_risk_score.sql
    └── fraud_05_early_claims.sql
```

---

## Setup Instructions

### Prerequisites
- Python 3.12+
- PostgreSQL 14+
- Power BI Desktop

### 1. Clone repository
```bash
git clone https://github.com/KousikaRavi/A-OEM-Enterprise-Analytics.git
cd A-OEM-Enterprise-Analytics
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and API key
```

### 5. Create databases
```sql
CREATE DATABASE aoem_warehouse ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE erp_db         ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE crm_db         ENCODING 'UTF8' TEMPLATE template0;
```

### 6. Run ETL pipeline in order
```bash
python etl_scripts/etl_geo.py            # Load geography dims
python etl_scripts/etl_dealer.py         # Load dealer dim
python etl_scripts/generate_crm_data.py  # Populate crm_db
```

### 7. Start CRM API
```bash
uvicorn crm_api.app:app --reload --port 8000
# Swagger docs at http://localhost:8000/docs
```

### 8. Run remaining ETL
```bash
python etl_scripts/etl_customer.py   # CRM API → dim_customer
python etl_scripts/etl_vehicle.py    # CRM API → dim_vehicle
```

### 9. Run simulation
```bash
python simulation/simulate_claims.py  # Generate 3000 warranty claims
```

### 10. Open Power BI
Connect to `aoem_warehouse` and open the `.pbix` file.

---

## Key Technical Decisions

**Why three separate source databases?**
Simulates real enterprise heterogeneous sources — internal ERP, external CRM, and flat files. Each requires a different ingestion pattern.

**Why FastAPI instead of direct DB connection for CRM?**
In production, external CRM systems expose APIs, not raw DB access. FastAPI simulates that boundary — same ETL code works whether the URL points to localhost or a Salesforce endpoint.

**Why plant data quality issues in source data?**
Real ETL always encounters dirty data. Planting known issues (mixed dates, dirty state names, orphan records) makes ETL transformation logic genuinely testable and demonstrates production-grade data handling.

**Why surrogate keys in warehouse?**
Source system business keys can change format or be reused. Surrogate keys decouple warehouse history from source system changes — standard Kimball dimensional modelling practice.

---

## Domain Background

Schema design and business logic are grounded in 4+ years of experience implementing Toyota Material Handling's Dealer Management System on SAP SD/CRM at Infosys — specifically dealer hierarchy topology, vehicle registration workflows, and warranty claim processing structures.

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
| Phase 7 | Power BI DirectQuery dashboard | ⏳ Upcoming |

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