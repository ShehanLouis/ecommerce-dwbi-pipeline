-- ====================================================================
-- IT3101 - Data Warehousing and Business Intelligence
-- OLAP ANALYTICAL QUERIES & BUSINESS INSIGHTS (Task 7 & Task 8)
-- Compatible with MS SQL Server (SSMS) & SQLite
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: EXECUTIVE SUMMARY KPIs (Report Page 1)
-- --------------------------------------------------------------------
SELECT 
    ROUND(SUM(item_price), 2) AS total_gmv_brl,
    ROUND(SUM(total_item_value), 2) AS total_sales_with_freight_brl,
    COUNT(DISTINCT order_id) AS total_unique_orders,
    COUNT(sales_fact_key) AS total_items_sold,
    ROUND(SUM(total_item_value) / COUNT(DISTINCT order_id), 2) AS average_order_value_aov,
    ROUND(AVG(review_score), 2) AS average_customer_satisfaction,
    ROUND(100.0 * SUM(CASE WHEN delivery_delay_days <= 0 THEN 1 ELSE 0 END) / 
          COUNT(CASE WHEN delivery_duration_days IS NOT NULL THEN 1 END), 2) AS on_time_delivery_rate_pct
FROM fact_order_sales_fulfillment;

-- --------------------------------------------------------------------
-- QUERY 2: MONTHLY TREND & SEASONALITY ANALYSIS (Report Page 2)
-- --------------------------------------------------------------------
SELECT 
    d.year_number,
    d.month_number,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.item_price), 2) AS monthly_gmv_brl,
    ROUND(AVG(f.delivery_duration_days), 1) AS avg_delivery_days,
    ROUND(AVG(f.review_score), 2) AS avg_monthly_review_score
FROM fact_order_sales_fulfillment f
JOIN dim_date d ON f.order_date_key = d.date_key
GROUP BY d.year_number, d.month_number, d.month_name
ORDER BY d.year_number, d.month_number;

-- --------------------------------------------------------------------
-- QUERY 3: REGIONAL LOGISTICS DISPARITY & FREIGHT INEQUITY (Insight 1)
-- --------------------------------------------------------------------
SELECT 
    c.customer_macro_region,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.item_price), 2) AS total_gmv,
    ROUND(100.0 * SUM(f.item_price) / (SELECT SUM(item_price) FROM fact_order_sales_fulfillment), 2) AS gmv_share_pct,
    ROUND(AVG(f.delivery_duration_days), 1) AS avg_delivery_days,
    ROUND(AVG(f.freight_value), 2) AS avg_freight_cost_brl,
    ROUND(AVG(f.freight_ratio) * 100, 2) AS freight_share_of_value_pct,
    ROUND(AVG(f.review_score), 2) AS avg_review_score
FROM fact_order_sales_fulfillment f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_order_status st ON f.status_key = st.status_key
WHERE st.is_delivered = 1
GROUP BY c.customer_macro_region
ORDER BY avg_delivery_days DESC;

-- --------------------------------------------------------------------
-- QUERY 4: THE "LATE DELIVERY PENALTY" ON REVIEW SCORES (Insight 2)
-- --------------------------------------------------------------------
SELECT 
    CASE 
        WHEN f.delivery_delay_days > 5 THEN 'Extremely Late (>5 Days)'
        WHEN f.delivery_delay_days > 0 THEN 'Slightly Late (1-5 Days)'
        WHEN f.delivery_delay_days = 0 THEN 'Exactly On Estimated Date'
        WHEN f.delivery_delay_days >= -5 THEN 'On Time (1-5 Days Early)'
        ELSE 'Super Fast (>5 Days Early)'
    END AS delivery_performance_bucket,
    COUNT(f.sales_fact_key) AS total_deliveries,
    ROUND(AVG(f.review_score), 2) AS average_review_score,
    ROUND(100.0 * SUM(CASE WHEN f.review_score = 5 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_5_star_reviews,
    ROUND(100.0 * SUM(CASE WHEN f.review_score = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_1_star_reviews
FROM fact_order_sales_fulfillment f
JOIN dim_order_status st ON f.status_key = st.status_key
WHERE st.is_delivered = 1 AND f.review_score IS NOT NULL
GROUP BY 
    CASE 
        WHEN f.delivery_delay_days > 5 THEN 'Extremely Late (>5 Days)'
        WHEN f.delivery_delay_days > 0 THEN 'Slightly Late (1-5 Days)'
        WHEN f.delivery_delay_days = 0 THEN 'Exactly On Estimated Date'
        WHEN f.delivery_delay_days >= -5 THEN 'On Time (1-5 Days Early)'
        ELSE 'Super Fast (>5 Days Early)'
    END
ORDER BY average_review_score DESC;

-- --------------------------------------------------------------------
-- QUERY 5: TOP 10 PRODUCT CATEGORIES BY GMV & SATISFACTION (Insight 3)
-- --------------------------------------------------------------------
SELECT 
    p.category_name_english AS product_category,
    COUNT(f.sales_fact_key) AS units_sold,
    ROUND(SUM(f.item_price), 2) AS total_gmv_brl,
    ROUND(AVG(f.item_price), 2) AS avg_unit_price,
    ROUND(AVG(f.review_score), 2) AS avg_review_score
FROM fact_order_sales_fulfillment f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name_english
ORDER BY total_gmv_brl DESC
LIMIT 10;

-- --------------------------------------------------------------------
-- QUERY 6: PAYMENT METHOD & INSTALLMENTS LEVERAGE (Insight 4)
-- --------------------------------------------------------------------
SELECT 
    pm.payment_type,
    pm.installments_tier,
    COUNT(DISTINCT f.order_id) AS order_count,
    ROUND(SUM(f.total_item_value), 2) AS total_revenue_brl,
    ROUND(AVG(f.total_item_value), 2) AS avg_ticket_size_brl
FROM fact_order_sales_fulfillment f
JOIN dim_payment_method pm ON f.payment_key = pm.payment_key
GROUP BY pm.payment_type, pm.installments_tier
ORDER BY total_revenue_brl DESC;

-- --------------------------------------------------------------------
-- QUERY 7: SELLER DISPATCH LATENCY VS CARRIER TRANSIT TIME (Insight 5)
-- --------------------------------------------------------------------
SELECT 
    CASE 
        WHEN f.seller_dispatch_delay_days > 0 THEN 'Late Seller Dispatch'
        ELSE 'On-Time Seller Dispatch'
    END AS seller_fulfillment_status,
    COUNT(f.sales_fact_key) AS order_items_count,
    ROUND(AVG(f.delivery_duration_days), 1) AS total_avg_delivery_days,
    ROUND(AVG(f.review_score), 2) AS avg_review_score
FROM fact_order_sales_fulfillment f
JOIN dim_order_status st ON f.status_key = st.status_key
WHERE st.is_delivered = 1 AND f.seller_dispatch_delay_days IS NOT NULL
GROUP BY 
    CASE 
        WHEN f.seller_dispatch_delay_days > 0 THEN 'Late Seller Dispatch'
        ELSE 'On-Time Seller Dispatch'
    END;
