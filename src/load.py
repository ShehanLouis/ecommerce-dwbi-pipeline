"""
Data Loading & Database Provisioning Module (Task 4, Task 5, Task 6)
Executes DDL schemas, loads staging and dimensional tables into the SQL Data Warehouse (SQLite),
creates Data Mart views, and exports clean datasets for Power BI.
"""

import os
import shutil
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(BASE_DIR, "sql")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
EXTERNAL_DIR = os.path.join(BASE_DIR, "data", "external")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
POWERBI_EXPORTS_DIR = os.path.join(BASE_DIR, "powerbi", "exports")
DB_PATH = os.path.join(BASE_DIR, "olist_dw.db")


def execute_sql_file(conn, filepath):
    print(f" -> Executing SQL: {os.path.basename(filepath)}...")
    with open(filepath, "r", encoding="utf-8") as f:
        sql_script = f.read()
    conn.executescript(sql_script)
    conn.commit()


def load_staging_tables(conn):
    print("\n" + "=" * 60)
    print("STEP 1: LOADING STAGING TABLES")
    print("=" * 60)
    staging_map = {
        "stg_orders": "olist_orders_dataset.csv",
        "stg_order_items": "olist_order_items_dataset.csv",
        "stg_customers": "olist_customers_dataset.csv",
        "stg_sellers": "olist_sellers_dataset.csv",
        "stg_products": "olist_products_dataset.csv",
        "stg_order_payments": "olist_order_payments_dataset.csv",
        "stg_order_reviews": "olist_order_reviews_dataset.csv",
        "stg_category_translation": "product_category_name_translation.csv"
    }

    for table_name, csv_file in staging_map.items():
        csv_path = os.path.join(RAW_DIR, csv_file)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f" -> Loaded {table_name}: {len(df):,} rows.")

    # Load JSON regional metadata into stg_brazil_regions
    import json
    json_path = os.path.join(EXTERNAL_DIR, "brazil_regions_metadata.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            geo_meta = json.load(f)["states"]
        rows = [
            {"state_code": k, "state_name": v["state_name"], "capital": v["capital"], 
             "macro_region": v["macro_region"], "logistics_zone": v["logistics_zone"]}
            for k, v in geo_meta.items()
        ]
        df_regions = pd.DataFrame(rows)
        df_regions.to_sql("stg_brazil_regions", conn, if_exists="replace", index=False)
        print(f" -> Loaded stg_brazil_regions: {len(df_regions):,} states.")


def load_dimensional_tables(conn):
    print("\n" + "=" * 60)
    print("STEP 2: LOADING DIMENSIONAL TABLES & FACT (STAR SCHEMA)")
    print("=" * 60)

    # 1. Dimensions First
    dim_tables = [
        ("dim_date", "dim_date.csv"),
        ("dim_customer", "dim_customer.csv"),
        ("dim_seller", "dim_seller.csv"),
        ("dim_product", "dim_product.csv"),
        ("dim_location", "dim_location.csv"),
        ("dim_payment_method", "dim_payment_method.csv"),
        ("dim_order_status", "dim_order_status.csv")
    ]

    for table_name, csv_file in dim_tables:
        csv_path = os.path.join(PROCESSED_DIR, csv_file)
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f" -> Loaded Dimension {table_name}: {len(df):,} rows.")

    # 2. Fact Table
    fact_path = os.path.join(PROCESSED_DIR, "fact_order_sales_fulfillment.csv")
    df_fact = pd.read_csv(fact_path)
    df_fact.to_sql("fact_order_sales_fulfillment", conn, if_exists="replace", index=False)
    print(f" -> Loaded Fact fact_order_sales_fulfillment: {len(df_fact):,} rows.")


def export_powerbi_datasets():
    print("\n" + "=" * 60)
    print("STEP 3: EXPORTING CLEAN CSVs FOR POWER BI")
    print("=" * 60)
    os.makedirs(POWERBI_EXPORTS_DIR, exist_ok=True)
    for fname in os.listdir(PROCESSED_DIR):
        if fname.endswith(".csv"):
            src = os.path.join(PROCESSED_DIR, fname)
            dst = os.path.join(POWERBI_EXPORTS_DIR, fname)
            shutil.copy2(src, dst)
            print(f" -> Exported {fname} to powerbi/exports/")


def run_loading():
    print("=" * 60)
    print("DATA WAREHOUSE INITIALIZATION & LOADING PIPELINE")
    print(f"Target Database: {DB_PATH}")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)

    # Step 1: DDL Execution
    execute_sql_file(conn, os.path.join(SQL_DIR, "01_staging_ddl.sql"))
    execute_sql_file(conn, os.path.join(SQL_DIR, "02_edw_star_schema_ddl.sql"))

    # Step 2: Ingest Staging
    load_staging_tables(conn)

    # Step 3: Ingest Star Schema
    load_dimensional_tables(conn)

    # Step 4: Create Data Mart Views
    print("\n" + "=" * 60)
    print("STEP 4: PROVISIONING DEPARTMENTAL DATA MARTS")
    print("=" * 60)
    execute_sql_file(conn, os.path.join(SQL_DIR, "03_data_marts_ddl.sql"))
    print(" -> Data Mart Views dm_logistics_operations_view and dm_sales_commercial_view created.")

    # Step 5: Export to Power BI
    export_powerbi_datasets()

    conn.close()
    print("\n" + "=" * 60)
    print("ALL LOADING TASKS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_loading()
