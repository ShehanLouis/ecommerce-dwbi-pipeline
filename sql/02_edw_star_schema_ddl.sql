-- ====================================================================
-- IT3101 - Data Warehousing and Business Intelligence
-- ENTERPRISE DATA WAREHOUSE (EDW) STAR SCHEMA DDL (Task 3 & Task 4)
-- Compatible with MS SQL Server (SSMS) & SQLite
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. DIMENSION: Date Dimension
-- Grain: One row per calendar day
-- Hierarchies: Year -> Quarter -> Month -> Day
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,                       -- Format: YYYYMMDD (e.g. 20171124)
    full_date DATE NOT NULL,                        -- YYYY-MM-DD
    day_of_month INT NOT NULL,                      -- 1 - 31
    day_name VARCHAR(15) NOT NULL,                  -- Monday, Tuesday...
    day_of_week INT NOT NULL,                       -- 1 (Monday) - 7 (Sunday)
    is_weekend INT NOT NULL,                        -- 1 = Weekend, 0 = Weekday
    month_number INT NOT NULL,                      -- 1 - 12
    month_name VARCHAR(15) NOT NULL,                -- January, February...
    quarter_number INT NOT NULL,                    -- 1 - 4
    quarter_name VARCHAR(10) NOT NULL,              -- Q1, Q2, Q3, Q4
    year_number INT NOT NULL,                       -- 2016, 2017, 2018...
    is_brazilian_holiday INT DEFAULT 0              -- 1 if public holiday in Brazil
);

-- --------------------------------------------------------------------
-- 2. DIMENSION: Customer Dimension
-- Grain: One row per customer record
-- Attributes: Demographic and geographic location
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INT PRIMARY KEY,                   -- Surrogate Key
    customer_id VARCHAR(50) NOT NULL,               -- Natural Key (Order-level)
    customer_unique_id VARCHAR(50) NOT NULL,        -- Natural Person Identifier
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(5),
    customer_macro_region VARCHAR(50)               -- Southeast, South, Northeast, North, Central-West
);

-- --------------------------------------------------------------------
-- 3. DIMENSION: Seller Dimension
-- Grain: One row per merchant/seller
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_seller (
    seller_key INT PRIMARY KEY,                     -- Surrogate Key
    seller_id VARCHAR(50) NOT NULL,                 -- Natural Key
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(100),
    seller_state VARCHAR(5),
    seller_macro_region VARCHAR(50)
);

-- --------------------------------------------------------------------
-- 4. DIMENSION: Product Dimension
-- Grain: One row per SKU/product
-- Hierarchies: Category -> Product
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_product (
    product_key INT PRIMARY KEY,                    -- Surrogate Key
    product_id VARCHAR(50) NOT NULL,                -- Natural Key
    category_name_portuguese VARCHAR(100),
    category_name_english VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g DECIMAL(10, 2),
    product_length_cm DECIMAL(10, 2),
    product_height_cm DECIMAL(10, 2),
    product_width_cm DECIMAL(10, 2),
    product_volume_cm3 DECIMAL(12, 2),
    weight_tier VARCHAR(20)                         -- Very Light, Light, Medium, Heavy, Extra Heavy
);

-- --------------------------------------------------------------------
-- 5. DIMENSION: Location Dimension
-- Grain: One row per zip code prefix (Centroid aggregated)
-- Hierarchies: Macro Region -> State -> City -> Zip Code Prefix
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_location (
    location_key INT PRIMARY KEY,                   -- Surrogate Key
    zip_code_prefix VARCHAR(10) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(5),
    macro_region VARCHAR(50),
    logistics_zone VARCHAR(50),
    avg_latitude DECIMAL(10, 6),
    avg_longitude DECIMAL(10, 6)
);

-- --------------------------------------------------------------------
-- 6. DIMENSION: Payment Method Dimension
-- Grain: One row per distinct payment method profile
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_payment_method (
    payment_key INT PRIMARY KEY,                    -- Surrogate Key
    payment_type VARCHAR(30) NOT NULL,              -- credit_card, boleto, voucher, debit_card
    installments_tier VARCHAR(30) NOT NULL          -- Single (1x), Short (2-4x), Medium (5-9x), Long (10x+)
);

-- --------------------------------------------------------------------
-- 7. DIMENSION: Order Status Dimension
-- Grain: One row per distinct status & fulfillment condition
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_order_status (
    status_key INT PRIMARY KEY,                     -- Surrogate Key
    order_status VARCHAR(30) NOT NULL,              -- delivered, shipped, canceled, invoiced...
    is_delivered INT NOT NULL,                      -- 1 = Yes, 0 = No
    is_delayed INT NOT NULL                         -- 1 = Delivered after estimated date, 0 = On-time
);

-- --------------------------------------------------------------------
-- 8. FACT TABLE: Fact Order Sales & Fulfillment
-- Grain: One row per individual order line item (order_id + order_item_id)
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_order_sales_fulfillment (
    sales_fact_key INT PRIMARY KEY,                 -- Surrogate Fact Key
    order_id VARCHAR(50) NOT NULL,                  -- Degenerate Dimension
    order_item_id INT NOT NULL,                     -- Degenerate Dimension
    
    -- Foreign Keys referencing Conformed Dimensions
    order_date_key INT NOT NULL,
    delivered_date_key INT,                         -- NULL if not yet delivered / canceled
    estimated_date_key INT NOT NULL,
    customer_key INT NOT NULL,
    seller_key INT NOT NULL,
    product_key INT NOT NULL,
    customer_location_key INT NOT NULL,
    payment_key INT NOT NULL,
    status_key INT NOT NULL,

    -- Additive Numerical Measures
    item_price DECIMAL(10, 2) NOT NULL,
    freight_value DECIMAL(10, 2) NOT NULL,
    total_item_value DECIMAL(10, 2) NOT NULL,       -- item_price + freight_value
    payment_value DECIMAL(10, 2) NOT NULL,

    -- Non-Additive / Semi-Additive & Derived Measures
    delivery_duration_days DECIMAL(10, 2),          -- delivered_date - purchase_date
    delivery_delay_days DECIMAL(10, 2),             -- delivered_date - estimated_date (+ve = late)
    seller_dispatch_delay_days DECIMAL(10, 2),      -- carrier_pickup - shipping_limit (+ve = late dispatch)
    freight_ratio DECIMAL(6, 4),                    -- freight_value / total_item_value
    review_score INT,                               -- 1 to 5 customer rating

    FOREIGN KEY (order_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (delivered_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (estimated_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (seller_key) REFERENCES dim_seller(seller_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (customer_location_key) REFERENCES dim_location(location_key),
    FOREIGN KEY (payment_key) REFERENCES dim_payment_method(payment_key),
    FOREIGN KEY (status_key) REFERENCES dim_order_status(status_key)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_fact_order_date ON fact_order_sales_fulfillment(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_order_sales_fulfillment(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_seller ON fact_order_sales_fulfillment(seller_key);
CREATE INDEX IF NOT EXISTS idx_fact_product ON fact_order_sales_fulfillment(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_status ON fact_order_sales_fulfillment(status_key);
