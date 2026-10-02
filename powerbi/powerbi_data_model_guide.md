# Power BI Implementation & Dashboard Construction Guide

This guide provides end-to-end instructions for loading the Kimball Star Schema datasets into **Microsoft Power BI Desktop**, configuring relationships, creating DAX measures, and constructing the 3 required report pages.

---

## Step 1: Ingesting Data into Power BI

1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Navigate to the folder: `c:\Users\sheha\Desktop\MODULES\S5\DW proj\powerbi\exports\`.
4. Import the following 8 CSV tables one by one (click **Load** for each):
   - `dim_date.csv`
   - `dim_customer.csv`
   - `dim_seller.csv`
   - `dim_product.csv`
   - `dim_location.csv`
   - `dim_payment_method.csv`
   - `dim_order_status.csv`
   - `fact_order_sales_fulfillment.csv`

---

## Step 2: Configuring Star Schema Relationships (Model View)

Switch to the **Model View** tab in Power BI and verify or create the following **1-to-Many ($1:*$) Single Direction** relationships:

| From Table (Dimension 1) | Dimension Key | To Table (Fact Many) | Fact Foreign Key | Cardinality | Cross Filter |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `dim_date` | `date_key` | `fact_order_sales_fulfillment` | `order_date_key` | 1 to Many ($1:*$) | Single |
| `dim_customer` | `customer_key` | `fact_order_sales_fulfillment` | `customer_key` | 1 to Many ($1:*$) | Single |
| `dim_seller` | `seller_key` | `fact_order_sales_fulfillment` | `seller_key` | 1 to Many ($1:*$) | Single |
| `dim_product` | `product_key` | `fact_order_sales_fulfillment` | `product_key` | 1 to Many ($1:*$) | Single |
| `dim_location` | `location_key` | `fact_order_sales_fulfillment` | `customer_location_key` | 1 to Many ($1:*$) | Single |
| `dim_payment_method` | `payment_key` | `fact_order_sales_fulfillment` | `payment_key` | 1 to Many ($1:*$) | Single |
| `dim_order_status` | `status_key` | `fact_order_sales_fulfillment` | `status_key` | 1 to Many ($1:*$) | Single |

---

## Step 3: Adding DAX Measures

1. In the **Report View**, right-click `fact_order_sales_fulfillment` in the Data pane and select **New Measure**.
2. Copy and paste each formula from [`powerbi/measures.dax`](file:///c:/Users/sheha/Desktop/MODULES/S5/DW%20proj/powerbi/measures.dax), including:
   - `Total GMV`
   - `Total Revenue with Freight`
   - `Total Orders`
   - `Average Order Value (AOV)`
   - `Average Review Score`
   - `On-Time Delivery Rate %`
   - `Average Delivery Days`

---

## Step 4: Constructing the 3 Report Pages

### Report Page 1: Executive Summary
- **Header**: "Olist E-Commerce Executive Overview"
- **Top KPI Cards (Row 1)**:
  - Card 1: `Total GMV` (Formatted as Currency R$ 13.59M)
  - Card 2: `Total Orders` (98.67K)
  - Card 3: `Average Order Value (AOV)` (R$ 160.58)
  - Card 4: `Average Review Score` (4.03 / 5.00)
  - Card 5: `On-Time Delivery Rate %` (92.1%)
- **Visual 1 (Donut Chart)**: GMV contribution by `dim_customer[customer_macro_region]`.
- **Visual 2 (Horizontal Clustered Bar Chart)**: Top 10 Product Categories by `[Total GMV]` from `dim_product[category_name_english]`.
- **Visual 3 (Column Chart)**: Total Orders by `dim_date[quarter_name]` across years.

### Report Page 2: Trend & Seasonality Analysis
- **Header**: "Sales Velocity, Seasonality & Operational Trend Analysis"
- **Visual 1 (Line & Clustered Column Chart)**:
  - X-Axis: `dim_date[year_number]` and `dim_date[month_name]`.
  - Column Values: `[Total GMV]` (showing the dramatic Black Friday spike in Nov 2017).
  - Line Values: `[Total Orders]`.
- **Visual 2 (Dual-Axis Line Chart)**:
  - X-Axis: `dim_date[year_number]` and `dim_date[month_number]`.
  - Line 1: `[Average Delivery Days]` (Logistics lead time).
  - Line 2: `[Average Review Score]` (Customer rating).
  - *Analytical Purpose*: Highlights the strong inverse relationship—as delivery transit times spike, customer satisfaction ratings plunge.
- **Visual 3 (Clustered Bar Chart)**: Year-over-Year GMV comparison by Quarter (`dim_date[quarter_name]`).

### Report Page 3: Interactive Drill-Down & Deep-Dive Analysis
- **Header**: "Operational Performance & Multi-Dimensional Deep-Dive"
- **Top Slicers / Filters**:
  - Date Range Slider: `dim_date[full_date]`
  - Dropdown Slicer: `dim_customer[customer_macro_region]`
  - Dropdown Slicer: `dim_product[category_name_english]`
  - Radio Slicer: `dim_payment_method[payment_type]`
- **Visual 1 (Hierarchy Matrix Table with Drill-down)**:
  - Rows Hierarchy: `dim_customer[customer_macro_region]` -> `dim_customer[customer_state]` -> `dim_customer[customer_city]`.
  - Columns: `[Total Orders]`, `[Total GMV]`, `[Average Delivery Days]`, `[Average Freight Cost]`, `[On-Time Delivery Rate %]`.
  - *Drill-down*: Allows users to click from Macro-Region down to State down to specific City.
- **Visual 2 (Scatter Plot / Bubble Chart)**:
  - X-Axis: `[Average Delivery Days]`
  - Y-Axis: `[Average Freight Cost]`
  - Bubble Size: `[Total Orders]`
  - Legend: `dim_customer[customer_macro_region]`
  - Details: `dim_customer[customer_state]`
  - *Analytical Purpose*: Immediately identifies outlying states in North/Northeast with excessive transit time and high freight fees.
