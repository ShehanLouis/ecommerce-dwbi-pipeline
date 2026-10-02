"""
Data Extraction Module (Task 2)
Extracts raw e-commerce data from primary operational files (CSV) and external metadata (JSON).
"""

import os
import json
import requests
import pandas as pd

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
EXTERNAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "external")

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Ajandaghian/olist-ecommerce-etl-pipeline/main/data/raw"

RAW_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
]


def download_file(filename: str, target_dir: str):
    target_path = os.path.join(target_dir, filename)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        print(f"[SKIP] {filename} already exists ({os.path.getsize(target_path):,} bytes).")
        return target_path

    url = f"{GITHUB_RAW_BASE}/{filename}"
    print(f"[DOWNLOADING] {filename} from {url}...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with open(target_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)

    print(f"[SAVED] {filename} ({os.path.getsize(target_path):,} bytes)")
    return target_path


def run_extraction():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(EXTERNAL_DATA_DIR, exist_ok=True)

    summary = {
        "status": "success",
        "sources": {}
    }

    print("=" * 60)
    print("STEP 1: EXTRACTING OPERATIONAL DATASETS (CSV)")
    print("=" * 60)

    for filename in RAW_FILES:
        filepath = download_file(filename, RAW_DATA_DIR)
        df = pd.read_csv(filepath)
        summary["sources"][filename] = {
            "type": "CSV",
            "rows": len(df),
            "columns": list(df.columns),
            "file_size_bytes": os.path.getsize(filepath)
        }
        print(f" -> {filename}: {len(df):,} rows, {len(df.columns)} columns")

    print("\n" + "=" * 60)
    print("STEP 2: EXTRACTING EXTERNAL REFERENCE METADATA (JSON)")
    print("=" * 60)
    json_path = os.path.join(EXTERNAL_DATA_DIR, "brazil_regions_metadata.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            geo_meta = json.load(f)
        summary["sources"]["brazil_regions_metadata.json"] = {
            "type": "JSON",
            "states_mapped": len(geo_meta.get("states", {})),
            "description": geo_meta.get("data_source_description")
        }
        print(f" -> brazil_regions_metadata.json: {len(geo_meta.get('states', {}))} Brazilian states mapped.")
    else:
        print("[ERROR] brazil_regions_metadata.json not found!")
        summary["status"] = "partial_error"

    # Save summary report
    summary_path = os.path.join(RAW_DATA_DIR, "extraction_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nExtraction complete. Summary saved to {summary_path}")
    return summary


if __name__ == "__main__":
    run_extraction()
