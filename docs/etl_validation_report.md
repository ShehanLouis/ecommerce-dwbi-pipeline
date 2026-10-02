# Automated ETL Pipeline & Data Warehouse Validation Report
**Date of Execution**: Automated Pipeline Execution
**Target Database**: `olist_dw.db` (Kimball Star Schema)

## 1. Row Count Reconciliation Across Layers
| Layer | Table Name | Record Count | Status |
| :--- | :--- | :--- | :--- |
| Staging | `stg_orders` | 99,441 | PASSED |
| Staging | `stg_order_items` | 112,650 | PASSED |
| Staging | `stg_customers` | 99,441 | PASSED |
| Staging | `stg_sellers` | 3,095 | PASSED |
| Staging | `stg_products` | 32,951 | PASSED |
| Staging | `stg_order_payments` | 103,886 | PASSED |
| Staging | `stg_order_reviews` | 99,224 | PASSED |
| Dimension | `dim_date` | 1,096 | PASSED |
| Dimension | `dim_customer` | 99,441 | PASSED |
| Dimension | `dim_seller` | 3,095 | PASSED |
| Dimension | `dim_product` | 32,951 | PASSED |
| Dimension | `dim_location` | 19,015 | PASSED |
| Dimension | `dim_payment_method` | 8 | PASSED |
| Dimension | `dim_order_status` | 9 | PASSED |
| Fact | `fact_order_sales_fulfillment` | 112,650 | PASSED |

## 2. Referential Integrity & Foreign Key Verification
Verifies that every foreign key in `fact_order_sales_fulfillment` successfully resolves to a valid primary key in the dimension tables.

| Fact Foreign Key | Dimension Table | Referenced Key | Orphan Count | Integrity Status |
| :--- | :--- | :--- | :--- | :--- |
| `order_date_key` | `dim_date` | `date_key` | 0 | PASSED (0 Orphans) |
| `customer_key` | `dim_customer` | `customer_key` | 0 | PASSED (0 Orphans) |
| `seller_key` | `dim_seller` | `seller_key` | 0 | PASSED (0 Orphans) |
| `product_key` | `dim_product` | `product_key` | 0 | PASSED (0 Orphans) |
| `customer_location_key` | `dim_location` | `location_key` | 0 | PASSED (0 Orphans) |
| `payment_key` | `dim_payment_method` | `payment_key` | 0 | PASSED (0 Orphans) |
| `status_key` | `dim_order_status` | `status_key` | 0 | PASSED (0 Orphans) |

## 3. Business Financial Metric Reconciliation
Ensures no financial value leakage between operational staging and the dimensional fact table.

| Metric | Staging Total (BRL) | Fact Table Total (BRL) | Variance (BRL) | Reconciliation Status |
| :--- | :--- | :--- | :--- | :--- |
| Item Price (GMV) | R$ 13,591,643.70 | R$ 13,591,643.70 | R$ 0.00 | PASSED (Exact Match) |
| Freight Value | R$ 2,251,909.54 | R$ 2,251,909.54 | R$ 0.00 | PASSED (Exact Match) |

## 4. Departmental Data Mart Verification
| Data Mart | Total Aggregated Rows | Total Orders Covered | Status |
| :--- | :--- | :--- | :--- |
| `dm_logistics_operations_view` | 34,124 | 98,127 | PASSED |
| `dm_sales_commercial_view` | 29,188 | 99,470 | PASSED |
