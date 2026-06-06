# A-OEM Enterprise Analytics Ecosystem

> **Project 03 · Self-built · In Progress**  
> PostgreSQL · Python · Power BI · Star Schema · ETL · Anomaly Detection

---

## Project Overview

An enterprise analytics simulation inspired directly by 4+ years of experience on **Toyota Material Handling's Dealer Management System (DMS)** at Infosys. This project simulates a forklift / material handling equipment distributor operating across Indian dealer networks — built to demonstrate production-grade data engineering and analytics skills.

**What makes this different from a tutorial project:**
Every design decision — the schema, the anomalies, the KPIs — mirrors real problems encountered in automotive dealer data. The planted anomalies are based on patterns seen in actual enterprise ERP environments.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    SOURCE SYSTEMS                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   ERP DB     │  │   CRM DB     │  │  CSV Files   │  │
│  │ (erp_db)     │  │ (crm_db)     │  │  (Dealers,   │  │
│  │ Orders,      │  │ Leads,       │  │   Products)  │  │
│  │ Warranty     │  │ Contacts     │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         └─────────────────┼─────────────────┘          │
│                           ▼                             │
│              ┌────────────────────────┐                 │
│              │    Python ETL Pipeline │                 │
│              │  (pandas · psycopg2)   │                 │
│              └────────────┬───────────┘                 │
│                           ▼                             │
│         ┌─────────────────────────────────┐             │
│         │     aoem_warehouse (PostgreSQL)  │             │
│         │         Star Schema             │             │
│         │  fact_sales · fact_warranty     │             │
│         │  dim_dealer · dim_product       │             │
│         │  dim_date · dim_geography       │             │
│         └─────────────────┬───────────────┘             │
│                           ▼                             │
│              ┌────────────────────────┐                 │
│              │   Power BI DirectQuery │                 │
│              │   Command Center       │                 │
│              └────────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

---

## Planted Business Anomalies

Three real-world business problems are deliberately embedded in the synthetic data for analytical detection:

| # | Anomaly | Type | Detection Method |
|---|---|---|---|
| 1 | West region revenue outlier | Performance | Z-score, MoM comparison |
| 2 | V-Max mast component defect cluster | Warranty | Claim frequency spike, part-level grouping |
| 3 | Fraudulent dealer duplicate warranty claims | Fraud | Duplicate detection, dealer-level aggregation |

---

## Project Phases

| Phase | What it covers | Status |
|---|---|---|
| **Phase 1** | PostgreSQL schema setup — 3 databases, star schema design | ✅ Complete |
| **Phase 2** | Synthetic data generation — 50 dealers, 5,000 vehicles, 15,000 claims | ✅ Complete |
| **Phase 3** | Python ETL pipeline — multi-source extraction, transformation, load | 🔄 In Progress |
| **Phase 4** | Anomaly injection — plant 3 business anomalies into clean data | ⏳ Upcoming |
| **Phase 5** | Diagnostic SQL — Z-score, window functions, anomaly detection queries | ⏳ Upcoming |
| **Phase 6** | Power BI DirectQuery dashboard — Command Center | ⏳ Upcoming |

---

## Folder Structure

```
A-OEM-Enterprise-Analytics/
│
├── 01_database_schema/          # SQL DDL scripts for all 3 databases
│   ├── aoem_warehouse.sql       # Star schema — fact + dimension tables
│   ├── erp_db.sql               # Source ERP schema
│   └── crm_db.sql               # Source CRM schema
│
├── 02_etl_pipeline/             # Python ETL scripts
│   ├── extract.py               # Pull from ERP, CRM, CSV sources
│   ├── transform.py             # Clean, standardise, apply business rules
│   └── load.py                  # Load into warehouse star schema
│
├── 03_synthetic_data/           # Data generation scripts
│   ├── generate_dealers.py      # 50 dealers across India
│   ├── generate_vehicles.py     # 5,000 vehicles with specs
│   ├── generate_warranty.py     # 15,000 warranty claims
│   └── plant_anomalies.py       # Inject 3 business anomalies
│
├── 04_sql_analytics/            # Diagnostic and analytical SQL
│   ├── kpi_queries.sql          # Revenue, warranty, dealer KPIs
│   ├── anomaly_detection.sql    # Z-score, outlier, duplicate queries
│   └── window_functions.sql     # MoM, ranking, running totals
│
├── 05_powerbi/                  # Power BI dashboard
│   └── AOEM_CommandCenter.pbix  # DirectQuery dashboard (coming soon)
│
├── docs/                        # Project documentation
│   └── data_dictionary.md       # Field definitions, business rules
│
├── .env.example                 # Credential template (copy to .env)
├── .gitignore                   # Excludes .env and other sensitive files
└── README.md                    # This file
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Warehouse** | PostgreSQL 15 |
| **ETL** | Python 3 — pandas, psycopg2, NumPy |
| **Synthetic Data** | Python — Faker, NumPy random |
| **Analytics** | SQL — Window Functions, CTEs, Z-score |
| **BI Dashboard** | Power BI Desktop — DirectQuery |
| **Dev Tools** | pgAdmin, VS Code, Git |

---

## Setup Instructions

### Prerequisites
- PostgreSQL 15+ installed and running
- Python 3.9+ with pip
- pgAdmin (optional but recommended)

### 1. Clone the repo
```bash
git clone https://github.com/KousikaRavi/A-OEM-Enterprise-Analytics.git
cd A-OEM-Enterprise-Analytics
```

### 2. Set up credentials
```bash
cp .env.example .env
# Open .env and fill in your PostgreSQL credentials
```

### 3. Create databases
```bash
# In pgAdmin or psql, run:
psql -U postgres -f 01_database_schema/aoem_warehouse.sql
psql -U postgres -f 01_database_schema/erp_db.sql
psql -U postgres -f 01_database_schema/crm_db.sql
```

### 4. Install Python dependencies
```bash
pip install pandas psycopg2-binary numpy faker python-dotenv
```

### 5. Run ETL
```bash
python 02_etl_pipeline/extract.py
python 02_etl_pipeline/transform.py
python 02_etl_pipeline/load.py
```

---

## Progress Log

| Date | What was done |
|---|---|
| Day 1 | PostgreSQL schema design — 3 databases, star schema, surrogate keys |
| Day 2 | Synthetic data generation — dealers, vehicles, warranty claims with planted anomalies |
| Day 3 | FastAPI mock CRM API setup · Uvicorn configuration |
| *(ongoing)* | ETL pipeline · Diagnostic SQL · Power BI dashboard |

---

## Portfolio Context

| # | Project | Stack | Status |
|---|---|---|---|
| MBA | Stock Clustering for Sector Analysis | Python · K-Means · PCA | ✅ Complete |
| 01 | Retail Sales Dashboard | Excel | ✅ Complete |
| 02 | ShopSphere Sales Analytics | MySQL · Power BI | ✅ Complete |
| 03 | **A-OEM Enterprise Analytics** ← You are here | PostgreSQL · Python · Power BI | 🔄 In Progress |

---

*Dataset is fully synthetic. No real Toyota, Infosys, or dealer data is used. All business scenarios are simulated for portfolio purposes.*