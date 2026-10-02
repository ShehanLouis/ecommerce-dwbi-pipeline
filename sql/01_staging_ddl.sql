-- ====================================================================
-- IT3101 - Data Warehousing and Business Intelligence
-- STAGING LAYER DDL (Task 2 & Task 3)
-- Operational Data Store / Staging Schema
-- Compatible with MS SQL Server (SSMS) & SQLite
-- ====================================================================

-- 1. Staging Orders Table
CREATE TABLE IF NOT EXISTS stg_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(20),
    order_purchase_timestamp VARCHAR(30),
    order_approved_at VARCHAR(30),
    order_delivered_carrier_date VARCHAR(30),
    order_delivered_customer_date VARCHAR(30),
    order_estimated_delivery_date VARCHAR(30)
);

-- 2. Staging Order Items Table
CREATE TABLE IF NOT EXISTS stg_order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date VARCHAR(30),
    price DECIMAL(10, 2),
    freight_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, order_item_id)
);

-- 3. Staging Customers Table
CREATE TABLE IF NOT EXISTS stg_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(5)
);

-- 4. Staging Sellers Table
CREATE TABLE IF NOT EXISTS stg_sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(100),
    seller_state VARCHAR(5)
);

-- 5. Staging Products Table
CREATE TABLE IF NOT EXISTS stg_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g DECIMAL(10, 2),
    product_length_cm DECIMAL(10, 2),
    product_height_cm DECIMAL(10, 2),
    product_width_cm DECIMAL(10, 2)
);

-- 6. Staging Payments Table
CREATE TABLE IF NOT EXISTS stg_order_payments (
    order_id VARCHAR(50),
    payment_sequential INT,
    payment_type VARCHAR(20),
    payment_installments INT,
    payment_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, payment_sequential)
);

-- 7. Staging Reviews Table
CREATE TABLE IF NOT EXISTS stg_order_reviews (
    review_id VARCHAR(50),
    order_id VARCHAR(50),
    review_score INT,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date VARCHAR(30),
    review_answer_timestamp VARCHAR(30)
);

-- 8. Staging Geolocation Table
CREATE TABLE IF NOT EXISTS stg_geolocation (
    geolocation_zip_code_prefix VARCHAR(10),
    geolocation_lat DECIMAL(10, 6),
    geolocation_lng DECIMAL(10, 6),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(5)
);

-- 9. Staging Category Translation Table
CREATE TABLE IF NOT EXISTS stg_category_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
);

-- 10. Staging Regional Metadata (From JSON Source)
CREATE TABLE IF NOT EXISTS stg_brazil_regions (
    state_code VARCHAR(5) PRIMARY KEY,
    state_name VARCHAR(100),
    capital VARCHAR(100),
    macro_region VARCHAR(50),
    logistics_zone VARCHAR(50)
);
