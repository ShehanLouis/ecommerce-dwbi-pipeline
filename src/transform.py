"""
Data Transformation & Dimensional Modeling Module (Task 4 & Task 5)
Cleans, standardizes, enriches, and structures data into a Kimball Star Schema.
"""

import os
import json
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
EXTERNAL_DIR = os.path.join(BASE_DIR, "data", "external")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def load_raw_data():
    print(" -> Loading raw CSVs and JSON metadata...")
    orders = pd.read_csv(os.path.join(RAW_DIR, "olist_orders_dataset.csv"))
    order_items = pd.read_csv(os.path.join(RAW_DIR, "olist_order_items_dataset.csv"))
    customers = pd.read_csv(os.path.join(RAW_DIR, "olist_customers_dataset.csv"))
    sellers = pd.read_csv(os.path.join(RAW_DIR, "olist_sellers_dataset.csv"))
    products = pd.read_csv(os.path.join(RAW_DIR, "olist_products_dataset.csv"))
    payments = pd.read_csv(os.path.join(RAW_DIR, "olist_order_payments_dataset.csv"))
    reviews = pd.read_csv(os.path.join(RAW_DIR, "olist_order_reviews_dataset.csv"))
    geo = pd.read_csv(os.path.join(RAW_DIR, "olist_geolocation_dataset.csv"))
    cat_trans = pd.read_csv(os.path.join(RAW_DIR, "product_category_name_translation.csv"))

    with open(os.path.join(EXTERNAL_DIR, "brazil_regions_metadata.json"), "r", encoding="utf-8") as f:
        geo_meta = json.load(f)["states"]

    return orders, order_items, customers, sellers, products, payments, reviews, geo, cat_trans, geo_meta


def transform_data():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    orders, order_items, customers, sellers, products, payments, reviews, geo, cat_trans, geo_meta = load_raw_data()

    print("\n" + "=" * 60)
    print("TRANSFORMATION 1: GEOLOCATION & LOCATION DIMENSION")
    print("=" * 60)
    # Deduplicate and aggregate geolocation to zip code prefix centroid
    geo_agg = geo.groupby("geolocation_zip_code_prefix").agg({
        "geolocation_lat": "mean",
        "geolocation_lng": "mean",
        "geolocation_city": "first",
        "geolocation_state": "first"
    }).reset_index()

    geo_agg.rename(columns={
        "geolocation_zip_code_prefix": "zip_code_prefix",
        "geolocation_lat": "avg_latitude",
        "geolocation_lng": "avg_longitude",
        "geolocation_city": "city",
        "geolocation_state": "state"
    }, inplace=True)

    # Standardize city names
    geo_agg["city"] = geo_agg["city"].astype(str).str.title().str.strip()
    geo_agg["state"] = geo_agg["state"].astype(str).str.upper().str.strip()

    # Map macro region and logistics zone
    geo_agg["macro_region"] = geo_agg["state"].map(lambda s: geo_meta.get(s, {}).get("macro_region", "Unknown"))
    geo_agg["logistics_zone"] = geo_agg["state"].map(lambda s: geo_meta.get(s, {}).get("logistics_zone", "Standard Zone"))

    geo_agg["location_key"] = np.arange(1, len(geo_agg) + 1)
    dim_location = geo_agg[["location_key", "zip_code_prefix", "city", "state", "macro_region", "logistics_zone", "avg_latitude", "avg_longitude"]]
    print(f" -> dim_location created: {len(dim_location):,} unique zip code centroids.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 2: CUSTOMER DIMENSION")
    print("=" * 60)
    customers["customer_city"] = customers["customer_city"].astype(str).str.title().str.strip()
    customers["customer_state"] = customers["customer_state"].astype(str).str.upper().str.strip()
    customers["customer_macro_region"] = customers["customer_state"].map(lambda s: geo_meta.get(s, {}).get("macro_region", "Unknown"))
    customers["customer_key"] = np.arange(1, len(customers) + 1)
    dim_customer = customers[["customer_key", "customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state", "customer_macro_region"]]
    print(f" -> dim_customer created: {len(dim_customer):,} customers.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 3: SELLER DIMENSION")
    print("=" * 60)
    sellers["seller_city"] = sellers["seller_city"].astype(str).str.title().str.strip()
    sellers["seller_state"] = sellers["seller_state"].astype(str).str.upper().str.strip()
    sellers["seller_macro_region"] = sellers["seller_state"].map(lambda s: geo_meta.get(s, {}).get("macro_region", "Unknown"))
    sellers["seller_key"] = np.arange(1, len(sellers) + 1)
    dim_seller = sellers[["seller_key", "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state", "seller_macro_region"]]
    print(f" -> dim_seller created: {len(dim_seller):,} sellers.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 4: PRODUCT DIMENSION")
    print("=" * 60)
    # Merge English category translation
    products = products.merge(cat_trans, on="product_category_name", how="left")
    products["product_category_name"] = products["product_category_name"].fillna("unknown")
    products["product_category_name_english"] = products["product_category_name_english"].fillna("Unknown").str.replace("_", " ").str.title()

    # Fill numeric columns
    products["product_name_lenght"] = products["product_name_lenght"].fillna(0).astype(int)
    products["product_description_lenght"] = products["product_description_lenght"].fillna(0).astype(int)
    products["product_photos_qty"] = products["product_photos_qty"].fillna(0).astype(int)
    products["product_weight_g"] = products["product_weight_g"].fillna(products["product_weight_g"].median())
    products["product_length_cm"] = products["product_length_cm"].fillna(products["product_length_cm"].median())
    products["product_height_cm"] = products["product_height_cm"].fillna(products["product_height_cm"].median())
    products["product_width_cm"] = products["product_width_cm"].fillna(products["product_width_cm"].median())

    # Derived attributes: Volume & Weight Tier
    products["product_volume_cm3"] = products["product_length_cm"] * products["product_height_cm"] * products["product_width_cm"]

    def assign_weight_tier(weight):
        if weight <= 500:
            return "Very Light (<0.5kg)"
        elif weight <= 2000:
            return "Light (0.5-2kg)"
        elif weight <= 5000:
            return "Medium (2-5kg)"
        elif weight <= 15000:
            return "Heavy (5-15kg)"
        else:
            return "Extra Heavy (>15kg)"

    products["weight_tier"] = products["product_weight_g"].apply(assign_weight_tier)
    products["product_key"] = np.arange(1, len(products) + 1)
    products.rename(columns={
        "product_category_name": "category_name_portuguese",
        "product_category_name_english": "category_name_english",
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length"
    }, inplace=True)

    dim_product = products[[
        "product_key", "product_id", "category_name_portuguese", "category_name_english",
        "product_name_length", "product_description_length", "product_photos_qty",
        "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm",
        "product_volume_cm3", "weight_tier"
    ]]
    print(f" -> dim_product created: {len(dim_product):,} products.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 5: DATE DIMENSION")
    print("=" * 60)
    # Generate comprehensive calendar from 2016-01-01 to 2018-12-31
    date_range = pd.date_range(start="2016-01-01", end="2018-12-31", freq="D")
    dim_date = pd.DataFrame({"full_date": date_range})
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["day_of_month"] = dim_date["full_date"].dt.day
    dim_date["day_name"] = dim_date["full_date"].dt.day_name()
    dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek + 1
    dim_date["is_weekend"] = dim_date["day_of_week"].apply(lambda d: 1 if d in [6, 7] else 0)
    dim_date["month_number"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["quarter_number"] = dim_date["full_date"].dt.quarter
    dim_date["quarter_name"] = "Q" + dim_date["quarter_number"].astype(str)
    dim_date["year_number"] = dim_date["full_date"].dt.year

    # Brazilian national holidays
    brazil_holidays = {
        "01-01", "04-21", "05-01", "09-07", "10-12", "11-02", "11-15", "12-25"
    }
    dim_date["is_brazilian_holiday"] = dim_date["full_date"].dt.strftime("%m-%d").apply(
        lambda md: 1 if md in brazil_holidays else 0
    )
    dim_date["full_date"] = dim_date["full_date"].dt.strftime("%Y-%m-%d")
    print(f" -> dim_date created: {len(dim_date):,} days.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 6: PAYMENT METHOD DIMENSION")
    print("=" * 60)
    def assign_installment_tier(inst):
        if inst <= 1:
            return "Single (1x)"
        elif inst <= 4:
            return "Short (2-4x)"
        elif inst <= 9:
            return "Medium (5-9x)"
        else:
            return "Long (10x+)"

    payments["installments_tier"] = payments["payment_installments"].apply(assign_installment_tier)
    
    # Order-level aggregated payment info
    order_payments_agg = payments.groupby("order_id").agg({
        "payment_type": "first",
        "payment_installments": "max",
        "payment_value": "sum",
        "installments_tier": "first"
    }).reset_index()

    # Dimension table of unique combinations
    dim_payment = order_payments_agg[["payment_type", "installments_tier"]].drop_duplicates().reset_index(drop=True)
    dim_payment["payment_key"] = np.arange(1, len(dim_payment) + 1)
    dim_payment = dim_payment[["payment_key", "payment_type", "installments_tier"]]
    print(f" -> dim_payment_method created: {len(dim_payment):,} payment profiles.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 7: ORDER STATUS DIMENSION")
    print("=" * 60)
    # Parse dates on orders to determine status attributes
    for col in ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date", "order_delivered_carrier_date"]:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    orders["is_delivered"] = (orders["order_status"] == "delivered").astype(int)
    orders["delivery_delay_days"] = (orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]).dt.total_seconds() / 86400.0
    orders["is_delayed"] = ((orders["delivery_delay_days"] > 0) & (orders["is_delivered"] == 1)).astype(int)

    dim_order_status = orders[["order_status", "is_delivered", "is_delayed"]].drop_duplicates().reset_index(drop=True)
    dim_order_status["status_key"] = np.arange(1, len(dim_order_status) + 1)
    dim_order_status = dim_order_status[["status_key", "order_status", "is_delivered", "is_delayed"]]
    print(f" -> dim_order_status created: {len(dim_order_status):,} status configurations.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 8: REVIEWS AGGREGATION")
    print("=" * 60)
    # Order-level review score (round average if multiple)
    order_reviews = reviews.groupby("order_id").agg({
        "review_score": "mean"
    }).reset_index()
    order_reviews["review_score"] = order_reviews["review_score"].round().astype(int)
    print(f" -> Reviews aggregated: {len(order_reviews):,} unique orders with reviews.")

    print("\n" + "=" * 60)
    print("TRANSFORMATION 9: FACT TABLE (FACT_ORDER_SALES_FULFILLMENT)")
    print("=" * 60)
    # Base merge: items + orders
    fact = order_items.merge(orders, on="order_id", how="inner")

    # Parse item dates
    fact["shipping_limit_date"] = pd.to_datetime(fact["shipping_limit_date"], errors="coerce")

    # Date Keys
    fact["order_date_key"] = fact["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype(float).fillna(0).astype(int)
    fact["delivered_date_key"] = fact["order_delivered_customer_date"].dt.strftime("%Y%m%d").astype(float)
    fact["delivered_date_key"] = fact["delivered_date_key"].apply(lambda x: int(x) if pd.notnull(x) else None)
    fact["estimated_date_key"] = fact["order_estimated_delivery_date"].dt.strftime("%Y%m%d").astype(float).fillna(0).astype(int)

    # Derived Measures
    fact["delivery_duration_days"] = (fact["order_delivered_customer_date"] - fact["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
    fact["delivery_duration_days"] = fact["delivery_duration_days"].round(2)

    fact["delivery_delay_days"] = (fact["order_delivered_customer_date"] - fact["order_estimated_delivery_date"]).dt.total_seconds() / 86400.0
    fact["delivery_delay_days"] = fact["delivery_delay_days"].round(2)

    fact["seller_dispatch_delay_days"] = (fact["order_delivered_carrier_date"] - fact["shipping_limit_date"]).dt.total_seconds() / 86400.0
    fact["seller_dispatch_delay_days"] = fact["seller_dispatch_delay_days"].round(2)

    fact["total_item_value"] = (fact["price"] + fact["freight_value"]).round(2)
    fact["freight_ratio"] = (fact["freight_value"] / fact["total_item_value"]).round(4)

    # Merge Foreign Keys
    # Customer Key & Location Key (via customer zip code prefix)
    cust_lookup = dim_customer[["customer_key", "customer_id", "customer_zip_code_prefix"]]
    fact = fact.merge(cust_lookup, on="customer_id", how="left")

    loc_lookup = dim_location[["location_key", "zip_code_prefix"]].rename(columns={"zip_code_prefix": "customer_zip_code_prefix"})
    fact = fact.merge(loc_lookup, on="customer_zip_code_prefix", how="left")
    fact["customer_location_key"] = fact["location_key"].fillna(1).astype(int)  # Fallback to key 1 if zip unmapped

    # Seller Key
    seller_lookup = dim_seller[["seller_key", "seller_id"]]
    fact = fact.merge(seller_lookup, on="seller_id", how="left")

    # Product Key
    prod_lookup = dim_product[["product_key", "product_id"]]
    fact = fact.merge(prod_lookup, on="product_id", how="left")

    # Payment Key & Value
    order_pay_with_key = order_payments_agg.merge(dim_payment, on=["payment_type", "installments_tier"], how="left")
    fact = fact.merge(order_pay_with_key[["order_id", "payment_key", "payment_value"]], on="order_id", how="left")
    fact["payment_key"] = fact["payment_key"].fillna(1).astype(int)
    fact["payment_value"] = fact["payment_value"].fillna(fact["total_item_value"]).round(2)

    # Status Key
    fact = fact.merge(dim_order_status[["status_key", "order_status", "is_delivered", "is_delayed"]], 
                      on=["order_status", "is_delivered", "is_delayed"], how="left")
    fact["status_key"] = fact["status_key"].fillna(1).astype(int)

    # Review Score
    fact = fact.merge(order_reviews, on="order_id", how="left")

    # Surrogate Fact Key
    fact["sales_fact_key"] = np.arange(1, len(fact) + 1)

    dim_fact = fact[[
        "sales_fact_key", "order_id", "order_item_id",
        "order_date_key", "delivered_date_key", "estimated_date_key",
        "customer_key", "seller_key", "product_key", "customer_location_key",
        "payment_key", "status_key",
        "price", "freight_value", "total_item_value", "payment_value",
        "delivery_duration_days", "delivery_delay_days", "seller_dispatch_delay_days",
        "freight_ratio", "review_score"
    ]].rename(columns={"price": "item_price"})

    print(f" -> fact_order_sales_fulfillment created: {len(dim_fact):,} fact rows.")

    # Save all transformed tables to processed CSVs
    print("\n" + "=" * 60)
    print("SAVING PROCESSED DIMENSIONAL DATASETS (CSV)")
    print("=" * 60)
    tables = {
        "dim_date.csv": dim_date,
        "dim_customer.csv": dim_customer,
        "dim_seller.csv": dim_seller,
        "dim_product.csv": dim_product,
        "dim_location.csv": dim_location,
        "dim_payment_method.csv": dim_payment,
        "dim_order_status.csv": dim_order_status,
        "fact_order_sales_fulfillment.csv": dim_fact
    }

    for name, df_table in tables.items():
        out_path = os.path.join(PROCESSED_DIR, name)
        df_table.to_csv(out_path, index=False)
        print(f" -> Saved {name}: {len(df_table):,} rows.")

    print("\nTransformation complete!")
    return tables


if __name__ == "__main__":
    transform_data()
