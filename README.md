# E-Commerce Data Warehouse & Business Intelligence Pipeline (`ecommerce-dwbi-pipeline`)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20MS%20SQL%20Server-orange.svg)](https://learn.microsoft.com/en-us/sql/ssms/sql-server-management-studio-ssms)
[![BI Tool](https://img.shields.io/badge/BI-Microsoft%20Power%20BI-yellow.svg)](https://powerbi.microsoft.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Kimball%20Star%20Schema-green.svg)](https://www.kimballgroup.com/)
[![Data Scale](https://img.shields.io/badge/Transactions-112K%20Line%20Items-blueviolet.svg)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

An end-to-end Enterprise Data Warehouse (EDW) and Business Intelligence (BI) platform engineered for the **Brazilian Multi-Vendor E-Commerce Public Dataset by Olist** (100,000+ orders from 2016 to 2018). 

The platform integrates heterogeneous operational data sources (Relational OLTP extracts + External IBGE Regional JSON metadata + Taxonomy translations) through an automated, modular Python ETL pipeline. It implements Ralph Kimball's dimensional modeling principles (Star Schema with 7 conformed dimensions and 1 fact table), provisions departmental Data Marts, and delivers executive and operational dashboards in **Microsoft Power BI**.

---

## 📌 Architectural Overview

The platform follows a 4-tier Kimball Enterprise Architecture:

![Enterprise DW Architecture](docs/diagrams/dw_architecture.png)

1. **Data Source Layer**: Ingests primary operational OLTP extracts (orders, items, customers, sellers, reviews, payments), external regional demographic metadata (`brazil_regions_metadata.json`), and catalog taxonomy mappings.
2. **Data Integration Layer (ETL Engine)**: Automated modular Python pipeline (`src/`) executing ingestion, geographic centroid deduplication (1M+ GPS logs $\rightarrow$ 19K zip centroids), ISO date parsing, surrogate key generation, and automated referential integrity validation.
3. **Storage Layer**: Relational schema hosting an operational Staging area (`STG_*`), an Enterprise Star Schema (`DIM_*` and `FACT_*`), and departmental Data Mart views (`DM_*`) for Logistics and Commercial teams.
4. **Presentation & Analytics Layer**: Power BI dashboards powered by a comprehensive DAX measure library, featuring Executive KPIs, time-series seasonality trends, and interactive multi-dimensional geographic drill-downs.

---

## 🌟 Dimensional Model (Star Schema)

The Enterprise Data Warehouse is modeled as a high-performance **Star Schema** centered on `fact_order_sales_fulfillment` (grain: **one row per individual order line item**):

![Kimball Star Schema](docs/diagrams/star_schema_diagram.png)

### Schema Components:
- **Central Fact Table**: `fact_order_sales_fulfillment` (112,650 line transactions)
  - *Additive Measures*: `item_price`, `freight_value`, `total_item_value`, `payment_value`
  - *Continuous / Derived Metrics*: `delivery_duration_days`, `delivery_delay_days`, `seller_dispatch_delay_days`, `freight_ratio`
  - *Sentiment Metric*: `review_score` (1 to 5 stars)
- **7 Conformed Dimension Tables**:
  - `dim_date`: Comprehensive calendar hierarchy (`Year` $\rightarrow$ `Quarter` $\rightarrow$ `Month` $\rightarrow$ `Day`) with Brazilian statutory holidays.
  - `dim_customer`: Unique customer profiles, cities, states, and IBGE macro-regions.
  - `dim_seller`: Registered merchant profiles and dispatch warehouse regions.
  - `dim_product`: Product catalog dimensions, volume (cm³), weights, and derived weight tiers.
  - `dim_location`: Spatial centroids (latitude/longitude), state capitals, and logistics zones.
  - `dim_payment_method`: Payment types (`credit_card`, `boleto`, `voucher`, `debit`) and installment brackets.
  - `dim_order_status`: Order lifecycle states and fulfillment SLA delay flags.

---

## 📊 Business Intelligence Dashboards (Microsoft Power BI)

The presentation layer is structured into three specialized analytical report pages:

| Report Page | Focus & Core Visualizations | Preview |
| :--- | :--- | :---: |
| **Page 1: Executive Summary** | **Macro Performance & Executive KPIs**: GMV (R$ 13.59M), Orders (98.6K), AOV (R$ 160.58), Review Score (4.03/5), On-Time Rate (92.1%), Regional Revenue Distribution Donut, and Top 10 Product Categories Bar Chart. | ![Executive Summary](docs/diagrams/page1_executive_summary.png) |
| **Page 2: Trend & Seasonality** | **Temporal Trajectory & Operational Correlations**: Monthly GMV/Volume trends showcasing Black Friday demand spikes (Nov 2017: R$ 1.01M), and dual-axis inverse correlation between delivery transit delays and customer review ratings. | ![Trend Analysis](docs/diagrams/page2_trend_analysis.png) |
| **Page 3: Interactive Deep-Dive** | **Multi-Dimensional Operational Exploration**: Interactive slicers (Date range, Macro-Region, State, Category, Payment Type), Geographic drill-down (`Region` $\rightarrow$ `State` $\rightarrow$ `City`), and State-level Delivery Days vs Freight Fee scatter analysis. | ![Interactive Analysis](docs/diagrams/page3_interactive_analysis.png) |

---

## 🔍 Key Data-Driven Insights

Analytical OLAP queries executed against the warehouse revealed critical operational dynamics:

1. **The "Late Delivery Penalty" on Customer Satisfaction**:
   - Deliveries completed on or before the estimated SLA date achieve an average satisfaction rating of **4.22 stars** (61.1% 5-star ratings; only 8.3% 1-star ratings).
   - Deliveries delayed beyond 5 days suffer a catastrophic collapse to **1.78 stars** (a **58% satisfaction drop**), with **67.55% of customers issuing 1-star ratings**. Delivery punctuality is the #1 driver of customer retention.
2. **Continental Logistics Inequities**:
   - Southeastern customers experience an average delivery lead time of **10.7 days** at an average freight fee of **R$ 17.34**.
   - Northern customers endure an average transit time of **22.6 days** (111% longer) at **R$ 36.80** (112% higher freight penalty). Remote states (Roraima, Amapá) face transit times exceeding **28 days**.
3. **Financing Elasticity on Basket Size**:
   - Single-installment purchases average **R$ 91.94**.
   - Long-term credit card financing (10x+ installments) expands basket size to **R$ 317.01**—a **245% increase** in Average Order Value (AOV).
4. **Pre-Transit Merchant Fulfillment Latency**:
   - **18.4% of total order fulfillment delay** occurs before the merchant transfers the package to the courier (`seller_dispatch_delay_days`), proving merchant dispatch SLAs are a major hidden leverage point.

---

## ⚡ 1-Click Quickstart & Reproduction

The entire platform is 100% reproducible. The automated pipeline downloads raw data on demand, processes it, creates the database, runs quality checks, and exports Power BI datasets in under **45 seconds**.

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/<your-username>/ecommerce-dwbi-pipeline.git
cd ecommerce-dwbi-pipeline
pip install -r requirements.txt
```

### 2. Run the End-to-End Pipeline
```bash
python run_pipeline.py
```
This single command executes:
- **`src/extract.py`**: Ingests the 9 raw Kaggle CSV files and external IBGE JSON metadata.
- **`src/transform.py`**: Cleans data, imputes nulls, aggregates 1M+ coordinates to centroids, and builds the Star Schema.
- **`src/load.py`**: Creates DDL schemas, loads Staging and Dimensional tables into `olist_dw.db`, and provisions Data Mart views.
- **`src/validate.py`**: Executes automated QA (referential integrity, 0 orphaned keys, exact financial reconciliation).
- **Power BI Export**: Exports clean dimensional CSVs into `powerbi/exports/`.

---

## 🗄️ SQL Server Management Studio (SSMS) Execution

The repository provides ANSI / T-SQL DDL scripts for deployment on **Microsoft SQL Server / SSMS**:
1. Open SSMS and create a new database:
   ```sql
   CREATE DATABASE Olist_DW;
   GO
   USE Olist_DW;
   GO
   ```
2. Execute the scripts in sequence:
   - [`sql/01_staging_ddl.sql`](sql/01_staging_ddl.sql): Creates operational staging tables.
   - [`sql/02_edw_star_schema_ddl.sql`](sql/02_edw_star_schema_ddl.sql): Creates Fact and 7 Dimension tables with PK/FK constraints.
   - [`sql/03_data_marts_ddl.sql`](sql/03_data_marts_ddl.sql): Creates Logistics and Sales Data Mart views.
   - [`sql/04_olap_analytical_queries.sql`](sql/04_olap_analytical_queries.sql): Executes the analytical business insight queries.

---

## 📈 Power BI Setup

1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Text/CSV** and select the 8 files from `powerbi/exports/`:
   `dim_date.csv`, `dim_customer.csv`, `dim_seller.csv`, `dim_product.csv`, `dim_location.csv`, `dim_payment_method.csv`, `dim_order_status.csv`, `fact_order_sales_fulfillment.csv`.
3. In Model View, configure 1-to-many single-directional relationships (see [`powerbi/powerbi_data_model_guide.md`](powerbi/powerbi_data_model_guide.md)).
4. Copy and paste the DAX calculation formulas from [`powerbi/measures.dax`](powerbi/measures.dax).

---

## 📁 Repository Structure

```
ecommerce-dwbi-pipeline/
│
├── README.md                                # Project overview, architecture & quickstart
├── requirements.txt                         # Python runtime dependencies
├── run_pipeline.py                          # 1-Click end-to-end pipeline orchestrator
├── .gitignore                               # Excludes large binaries (>100MB) & raw data
│
├── data/
│   ├── raw/                                 # Raw downloaded Olist CSVs (auto-generated)
│   ├── external/
│   │   └── brazil_regions_metadata.json     # IBGE 27 Brazilian states & macro-regions
│   └── processed/                           # Cleansed Star Schema CSV datasets
│
├── sql/
│   ├── 01_staging_ddl.sql                   # Staging tables DDL (SSMS & SQLite compatible)
│   ├── 02_edw_star_schema_ddl.sql           # Kimball Star Schema Fact & Dimensions DDL
│   ├── 03_data_marts_ddl.sql                # Departmental Data Mart views (Logistics & Sales)
│   └── 04_olap_analytical_queries.sql       # Analytical OLAP queries for business insights
│
├── src/
│   ├── __init__.py
│   ├── extract.py                           # Multi-source ingestion & audit
│   ├── transform.py                         # Cleansing, spatial centroids, derived metrics
│   ├── load.py                              # DB provisioning & surrogate mapping
│   ├── validate.py                          # Automated QA (0 orphan keys, financial match)
│   └── generate_visuals.py                  # Generates 300 DPI architecture & BI diagrams
│
├── powerbi/
│   ├── measures.dax                         # Complete DAX formula library for Power BI
│   ├── powerbi_data_model_guide.md          # Step-by-step Power BI import & modeling guide
│   └── exports/                             # Clean CSVs ready for 1-click import into Power BI
│
└── docs/
    ├── ARCHITECTURE_AND_ANALYTICS_REPORT.md # Full technical architecture & analytics paper
    ├── etl_validation_report.md             # Automated validation test results
    └── diagrams/                            # High-resolution architectural figures
        ├── dw_architecture.png              # 4-Tier Kimball DW architecture diagram
        ├── star_schema_diagram.png          # Star Schema ER diagram
        ├── page1_executive_summary.png      # Power BI Dashboard Page 1 mockup
        ├── page2_trend_analysis.png         # Power BI Dashboard Page 2 mockup
        └── page3_interactive_analysis.png   # Power BI Dashboard Page 3 mockup
```

---

## 📄 Documentation & Validation Reports
- **Full Architecture & Analytics Whitepaper**: [`docs/ARCHITECTURE_AND_ANALYTICS_REPORT.md`](docs/ARCHITECTURE_AND_ANALYTICS_REPORT.md)
- **Automated Validation Results**: [`docs/etl_validation_report.md`](docs/etl_validation_report.md)
- **Power BI Modeling Guide**: [`powerbi/powerbi_data_model_guide.md`](powerbi/powerbi_data_model_guide.md)
