-- ====================================================================
-- IT3101 - Data Warehousing and Business Intelligence
-- DEPARTMENT-SPECIFIC DATA MARTS DDL (Task 6)
-- Compatible with MS SQL Server (SSMS) & SQLite
-- ====================================================================

-- --------------------------------------------------------------------
-- DATA MART 1: Logistics & Supply Chain Operations Data Mart
-- Target Users: VP of Supply Chain, Logistics Directors, Carrier Managers
-- Purpose: Monitor carrier fulfillment, delivery lead times, regional freight costs,
--          and the impact of transit delays on customer satisfaction.
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS dm_logistics_operations_view;
CREATE VIEW dm_logistics_operations_view AS
SELECT
    d.year_number,
    d.quarter_name,
    d.month_name,
    d.month_number,
    c.customer_macro_region AS destination_macro_region,
    c.customer_state AS destination_state,
    s.seller_state AS origin_state,
    p.category_name_english AS product_category,
    p.weight_tier,
    COUNT(f.sales_fact_key) AS total_items_shipped,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(AVG(f.delivery_duration_days), 2) AS avg_delivery_days,
    ROUND(AVG(f.delivery_delay_days), 2) AS avg_delay_vs_estimated_days,
    ROUND(AVG(f.seller_dispatch_delay_days), 2) AS avg_seller_dispatch_days,
    ROUND(AVG(f.freight_value), 2) AS avg_freight_cost,
    ROUND(SUM(f.freight_value), 2) AS total_freight_revenue,
    ROUND(AVG(f.freight_ratio) * 100, 2) AS avg_freight_percent_of_value,
    ROUND(AVG(f.review_score), 2) AS avg_customer_review_score,
    SUM(CASE WHEN f.delivery_delay_days > 0 THEN 1 ELSE 0 END) AS delayed_deliveries_count,
    ROUND(100.0 * SUM(CASE WHEN f.delivery_delay_days <= 0 THEN 1 ELSE 0 END) / COUNT(f.sales_fact_key), 2) AS on_time_delivery_rate_pct
FROM fact_order_sales_fulfillment f
JOIN dim_date d ON f.order_date_key = d.date_key
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_seller s ON f.seller_key = s.seller_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_order_status st ON f.status_key = st.status_key
WHERE st.is_delivered = 1
GROUP BY
    d.year_number,
    d.quarter_name,
    d.month_name,
    d.month_number,
    c.customer_macro_region,
    c.customer_state,
    s.seller_state,
    p.category_name_english,
    p.weight_tier;

-- --------------------------------------------------------------------
-- DATA MART 2 (BONUS): Sales & Commercial Performance Data Mart
-- Target Users: Chief Commercial Officer (CCO), Category Managers, Marketing
-- Purpose: Track revenue velocity, Average Order Value (AOV), payment method
--          adoption, top product categories, and regional customer demand.
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS dm_sales_commercial_view;
CREATE VIEW dm_sales_commercial_view AS
SELECT
    d.year_number,
    d.quarter_name,
    d.month_name,
    d.month_number,
    c.customer_macro_region,
    c.customer_state,
    p.category_name_english AS product_category,
    pm.payment_type,
    pm.installments_tier,
    COUNT(f.sales_fact_key) AS total_items_sold,
    COUNT(DISTINCT f.order_id) AS total_orders_placed,
    COUNT(DISTINCT c.customer_unique_id) AS distinct_buyers_count,
    ROUND(SUM(f.item_price), 2) AS gross_merchandise_value_gmv,
    ROUND(SUM(f.total_item_value), 2) AS total_order_value_with_freight,
    ROUND(AVG(f.item_price), 2) AS avg_item_price,
    ROUND(SUM(f.total_item_value) / COUNT(DISTINCT f.order_id), 2) AS avg_order_value_aov,
    ROUND(AVG(f.review_score), 2) AS avg_review_score
FROM fact_order_sales_fulfillment f
JOIN dim_date d ON f.order_date_key = d.date_key
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_payment_method pm ON f.payment_key = pm.payment_key
GROUP BY
    d.year_number,
    d.quarter_name,
    d.month_name,
    d.month_number,
    c.customer_macro_region,
    c.customer_state,
    p.category_name_english,
    pm.payment_type,
    pm.installments_tier;
