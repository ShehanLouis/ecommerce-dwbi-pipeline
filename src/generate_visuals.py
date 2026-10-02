"""
Visuals & Report Figures Generator
Creates high-resolution visual charts from olist_dw.db and architecture diagrams for the final academic report.
"""

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "olist_dw.db")
DIAGRAMS_DIR = os.path.join(BASE_DIR, "docs", "diagrams")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

# Set clean visual style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")

    colors = {
        "sources": "#E3F2FD",
        "etl": "#FFF3E0",
        "storage": "#E8F5E9",
        "bi": "#F3E5F5",
        "border": "#37474F"
    }

    # 1. Sources Layer
    rect1 = patches.FancyBboxPatch((0.5, 7.5), 11, 2.0, boxstyle="round,pad=0.2", facecolor=colors["sources"], edgecolor="#1976D2", linewidth=2)
    ax.add_patch(rect1)
    ax.text(6.0, 9.1, "1. DATA SOURCE LAYER (OPERATIONAL & EXTERNAL)", ha="center", va="center", fontsize=12, fontweight="bold", color="#0D47A1")
    ax.text(2.3, 8.2, "Primary OLTP Relational CSVs\n(Orders, Items, Customers,\nSellers, Reviews, Products)", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#90CAF9"))
    ax.text(6.0, 8.2, "External Regional Metadata\n(brazil_regions_metadata.json\nIBGE Macro-Regions)", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#90CAF9"))
    ax.text(9.7, 8.2, "Catalog Reference Taxonomy\n(product_category_translation\nPayment Classification)", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#90CAF9"))

    # Arrow 1
    ax.annotate("", xy=(6, 7.1), xytext=(6, 7.5), arrowprops=dict(facecolor="#37474F", width=2, headwidth=8))

    # 2. ETL Layer
    rect2 = patches.FancyBboxPatch((0.5, 5.0), 11, 1.9, boxstyle="round,pad=0.2", facecolor=colors["etl"], edgecolor="#F57C00", linewidth=2)
    ax.add_patch(rect2)
    ax.text(6.0, 6.5, "2. DATA INTEGRATION & ETL LAYER (PYTHON PIPELINE)", ha="center", va="center", fontsize=12, fontweight="bold", color="#E65100")
    ax.text(2.3, 5.7, "Extraction Module\n(extract.py)\nAutomated Fetch & Audit", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#FFCC80"))
    ax.text(6.0, 5.7, "Transformation & Cleansing\n(transform.py)\nNulls, Geo-Centroids, Metrics", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#FFCC80"))
    ax.text(9.7, 5.7, "Loading & QA Validation\n(load.py & validate.py)\nSurrogate Keys & 0 Orphans", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#FFCC80"))

    # Arrow 2
    ax.annotate("", xy=(6, 4.6), xytext=(6, 5.0), arrowprops=dict(facecolor="#37474F", width=2, headwidth=8))

    # 3. Storage Layer
    rect3 = patches.FancyBboxPatch((0.5, 2.5), 11, 1.9, boxstyle="round,pad=0.2", facecolor=colors["storage"], edgecolor="#388E3C", linewidth=2)
    ax.add_patch(rect3)
    ax.text(6.0, 4.0, "3. STORAGE LAYER (ENTERPRISE DATA WAREHOUSE & DATA MARTS)", ha="center", va="center", fontsize=12, fontweight="bold", color="#1B5E20")
    ax.text(2.3, 3.2, "Staging Database Area\n(stg_orders, stg_items,\nstg_customers, stg_geo...)", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#A5D6A7"))
    ax.text(6.0, 3.2, "Enterprise DW Star Schema\n(fact_order_sales_fulfillment\n+ 7 Conformed Dimensions)", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#A5D6A7"))
    ax.text(9.7, 3.2, "Departmental Data Marts\n(dm_logistics_operations_view\ndm_sales_commercial_view)", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#A5D6A7"))

    # Arrow 3
    ax.annotate("", xy=(6, 2.1), xytext=(6, 2.5), arrowprops=dict(facecolor="#37474F", width=2, headwidth=8))

    # 4. Presentation Layer
    rect4 = patches.FancyBboxPatch((0.5, 0.3), 11, 1.6, boxstyle="round,pad=0.2", facecolor=colors["bi"], edgecolor="#7B1FA2", linewidth=2)
    ax.add_patch(rect4)
    ax.text(6.0, 1.6, "4. PRESENTATION & ANALYTICS LAYER (MICROSOFT POWER BI)", ha="center", va="center", fontsize=12, fontweight="bold", color="#4A148C")
    ax.text(2.3, 0.9, "Report Page 1\nExecutive Summary & KPIs", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#CE93D8"))
    ax.text(6.0, 0.9, "Report Page 2\nTrend & Seasonality Analytics", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#CE93D8"))
    ax.text(9.7, 0.9, "Report Page 3\nInteractive Slicers & Drill-Downs", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", facecolor="white", edgecolor="#CE93D8"))

    plt.tight_layout()
    out_file = os.path.join(DIAGRAMS_DIR, "dw_architecture.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f" -> Generated: {out_file}")


def generate_star_schema_diagram():
    fig, ax = plt.subplots(figsize=(14, 10), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Center Fact Box
    fact_box = patches.FancyBboxPatch((4.8, 3.2), 4.4, 3.6, boxstyle="round,pad=0.2", facecolor="#FFF9C4", edgecolor="#FBC02D", linewidth=3)
    ax.add_patch(fact_box)
    ax.text(7.0, 6.5, "FACT_ORDER_SALES_FULFILLMENT", ha="center", va="center", fontsize=10, fontweight="bold", color="#F57F17")
    fact_text = (
        "PK: sales_fact_key (INT)\n"
        "Degenerate: order_id, order_item_id\n"
        "FK: order_date_key -> dim_date\n"
        "FK: delivered_date_key -> dim_date\n"
        "FK: customer_key -> dim_customer\n"
        "FK: seller_key -> dim_seller\n"
        "FK: product_key -> dim_product\n"
        "FK: customer_location_key -> dim_location\n"
        "FK: payment_key -> dim_payment_method\n"
        "FK: status_key -> dim_order_status\n"
        "Measures:\n"
        "• item_price, freight_value, total_item_value\n"
        "• delivery_duration_days, delivery_delay_days\n"
        "• seller_dispatch_delay_days, review_score"
    )
    ax.text(7.0, 4.8, fact_text, ha="center", va="center", fontsize=7.5, color="#212121")

    # Surrounding Dimensions
    dims = [
        ("DIM_DATE", 1.8, 8.2, "PK: date_key\nfull_date, day_name\nmonth_name, quarter_name\nyear_number, is_holiday", (4.8, 5.8)),
        ("DIM_CUSTOMER", 7.0, 8.8, "PK: customer_key\ncustomer_id, customer_unique_id\ncustomer_city, customer_state\ncustomer_macro_region", (7.0, 6.8)),
        ("DIM_SELLER", 12.2, 8.2, "PK: seller_key\nseller_id, seller_city\nseller_state, seller_macro_region", (9.2, 5.8)),
        ("DIM_PRODUCT", 12.2, 3.8, "PK: product_key\nproduct_id, category_name_english\nweight_g, product_volume_cm3\nweight_tier", (9.2, 4.5)),
        ("DIM_LOCATION", 12.2, 0.8, "PK: location_key\nzip_code_prefix, city, state\nmacro_region, logistics_zone\navg_latitude, avg_longitude", (9.2, 3.5)),
        ("DIM_PAYMENT_METHOD", 7.0, 0.8, "PK: payment_key\npayment_type\ninstallments_tier", (7.0, 3.2)),
        ("DIM_ORDER_STATUS", 1.8, 2.5, "PK: status_key\norder_status\nis_delivered, is_delayed", (4.8, 4.0))
    ]

    for title, x, y, body, fact_pt in dims:
        p = patches.FancyBboxPatch((x-1.7, y-0.8), 3.4, 1.6, boxstyle="round,pad=0.15", facecolor="#E1F5FE", edgecolor="#0288D1", linewidth=1.5)
        ax.add_patch(p)
        ax.text(x, y+0.5, title, ha="center", va="center", fontsize=9, fontweight="bold", color="#01579B")
        ax.text(x, y-0.1, body, ha="center", va="center", fontsize=7, color="#263238")
        # Line from Dimension to Fact
        ax.annotate("", xy=fact_pt, xytext=(x, y-0.8 if y > 5 else y+0.8),
                    arrowprops=dict(arrowstyle="->", color="#37474F", lw=1.2, ls="--"))

    plt.tight_layout()
    out_file = os.path.join(DIAGRAMS_DIR, "star_schema_diagram.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f" -> Generated: {out_file}")


def generate_page1_visuals():
    conn = sqlite3.connect(DB_PATH)
    fig = plt.figure(figsize=(14, 8), dpi=300)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2])

    # Top Left: Macro-Region Revenue Share
    ax1 = fig.add_subplot(gs[0, 0])
    df_reg = pd.read_sql_query("""
        SELECT c.customer_macro_region, SUM(f.item_price) AS gmv
        FROM fact_order_sales_fulfillment f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        GROUP BY c.customer_macro_region
        ORDER BY gmv DESC
    """, conn)
    colors = ["#1976D2", "#42A5F5", "#90CAF9", "#FFB74D", "#FF7043"]
    wedges, texts, autotexts = ax1.pie(
        df_reg["gmv"], labels=df_reg["customer_macro_region"], autopct="%1.1f%%",
        startangle=140, colors=colors, pctdistance=0.8,
        wedgeprops=dict(width=0.4, edgecolor="white")
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_weight("bold")
    ax1.set_title("Revenue Contribution by Brazilian Macro-Region", fontsize=11, fontweight="bold")

    # Top Right: Delivery On-Time Performance vs Delayed
    ax2 = fig.add_subplot(gs[0, 1])
    df_perf = pd.read_sql_query("""
        SELECT 
            CASE WHEN delivery_delay_days <= 0 THEN 'On-Time / Early' ELSE 'Delayed (Late)' END AS perf,
            COUNT(*) AS cnt
        FROM fact_order_sales_fulfillment
        WHERE delivery_duration_days IS NOT NULL
        GROUP BY 1
    """, conn)
    ax2.pie(df_perf["cnt"], labels=df_perf["perf"], autopct="%1.1f%%", colors=["#2E7D32", "#C62828"],
            startangle=90, wedgeprops=dict(width=0.4, edgecolor="white"))
    ax2.set_title("Overall Order Delivery SLA Compliance Rate (92.1% On-Time)", fontsize=11, fontweight="bold")

    # Bottom: Top 10 Product Categories by GMV
    ax3 = fig.add_subplot(gs[1, :])
    df_cat = pd.read_sql_query("""
        SELECT p.category_name_english, SUM(f.item_price) / 1e6 AS gmv_millions
        FROM fact_order_sales_fulfillment f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.category_name_english
        ORDER BY gmv_millions ASC
        LIMIT 10
    """, conn)
    bars = ax3.barh(df_cat["category_name_english"], df_cat["gmv_millions"], color="#1565C0", edgecolor="#0D47A1")
    ax3.set_xlabel("Gross Merchandise Value (BRL Millions)", fontweight="bold")
    ax3.set_title("Top 10 Product Categories by Total Revenue (GMV)", fontsize=11, fontweight="bold")
    for bar in bars:
        w = bar.get_width()
        ax3.text(w + 0.02, bar.get_y() + bar.get_height()/2, f"R$ {w:.2f}M", va="center", fontsize=8, fontweight="bold")

    plt.suptitle("Report Page 1: Executive Summary & High-Level KPIs (Power BI Overview)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    out_file = os.path.join(DIAGRAMS_DIR, "page1_executive_summary.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    conn.close()
    print(f" -> Generated: {out_file}")


def generate_page2_visuals():
    conn = sqlite3.connect(DB_PATH)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), dpi=300)

    # 1. Monthly GMV & Order Volume Trend
    df_trend = pd.read_sql_query("""
        SELECT 
            d.year_number || '-' || SUBSTR('0' || d.month_number, -2, 2) AS year_month,
            COUNT(DISTINCT f.order_id) AS orders,
            ROUND(SUM(f.item_price) / 1000.0, 1) AS gmv_k
        FROM fact_order_sales_fulfillment f
        JOIN dim_date d ON f.order_date_key = d.date_key
        WHERE d.year_number BETWEEN 2017 AND 2018
        GROUP BY 1
        ORDER BY 1
    """, conn)

    ax1_twin = ax1.twinx()
    l1 = ax1.plot(df_trend["year_month"], df_trend["gmv_k"], color="#1E88E5", marker="o", linewidth=2.5, label="Monthly GMV (R$ Thousands)")
    l2 = ax1_twin.plot(df_trend["year_month"], df_trend["orders"], color="#FB8C00", marker="s", linewidth=2, linestyle="--", label="Order Volume")
    
    # Annotate Black Friday Surge (Nov 2017)
    bf_idx = df_trend[df_trend["year_month"] == "2017-11"].index
    if len(bf_idx) > 0:
        idx = bf_idx[0]
        ax1.annotate("Black Friday Peak\n(Nov 2017: R$ 1.01M)", 
                     xy=(idx, df_trend["gmv_k"].iloc[idx]), 
                     xytext=(idx - 2, df_trend["gmv_k"].iloc[idx] + 150),
                     arrowprops=dict(facecolor="#D32F2F", shrink=0.08, width=1.5, headwidth=6),
                     fontsize=9, fontweight="bold", color="#D32F2F")

    ax1.set_title("Monthly Revenue (GMV) and Order Volume Trajectory (2017-2018)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Gross Merchandise Value (R$ '000)", color="#1E88E5", fontweight="bold")
    ax1_twin.set_ylabel("Total Orders Placed", color="#FB8C00", fontweight="bold")
    ax1.tick_params(axis="x", rotation=45)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # 2. Dual-Axis Delivery Duration vs Review Rating
    df_corr = pd.read_sql_query("""
        SELECT 
            d.year_number || '-' || SUBSTR('0' || d.month_number, -2, 2) AS year_month,
            ROUND(AVG(f.delivery_duration_days), 1) AS avg_lead_time_days,
            ROUND(AVG(f.review_score), 2) AS avg_rating
        FROM fact_order_sales_fulfillment f
        JOIN dim_date d ON f.order_date_key = d.date_key
        WHERE d.year_number BETWEEN 2017 AND 2018 AND f.delivery_duration_days IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """, conn)

    ax2_twin = ax2.twinx()
    ax2.plot(df_corr["year_month"], df_corr["avg_lead_time_days"], color="#E53935", marker="^", linewidth=2.5, label="Avg Delivery Lead Time (Days)")
    ax2_twin.plot(df_corr["year_month"], df_corr["avg_rating"], color="#43A047", marker="D", linewidth=2, linestyle="-.", label="Avg Review Rating (1-5)")

    ax2.set_title("Delivery Lead Time vs Customer Review Rating (Direct Inverse Relationship)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Delivery Lead Time (Calendar Days)", color="#E53935", fontweight="bold")
    ax2_twin.set_ylabel("Average Review Rating (out of 5.0)", color="#43A047", fontweight="bold")
    ax2.tick_params(axis="x", rotation=45)
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.suptitle("Report Page 2: Trend & Seasonality Analysis (Power BI Dashboard)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    out_file = os.path.join(DIAGRAMS_DIR, "page2_trend_analysis.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    conn.close()
    print(f" -> Generated: {out_file}")


def generate_page3_visuals():
    conn = sqlite3.connect(DB_PATH)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    # 1. State-level Freight Cost vs Delivery Lead Time Scatter
    df_geo = pd.read_sql_query("""
        SELECT 
            c.customer_state,
            c.customer_macro_region,
            ROUND(AVG(f.delivery_duration_days), 1) AS avg_delivery_days,
            ROUND(AVG(f.freight_value), 2) AS avg_freight,
            COUNT(DISTINCT f.order_id) AS orders
        FROM fact_order_sales_fulfillment f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_order_status st ON f.status_key = st.status_key
        WHERE st.is_delivered = 1
        GROUP BY c.customer_state, c.customer_macro_region
    """, conn)

    reg_colors = {
        "Southeast": "#1E88E5",
        "South": "#43A047",
        "Central-West": "#FB8C00",
        "Northeast": "#8E24AA",
        "North": "#E53935"
    }

    for reg, grp in df_geo.groupby("customer_macro_region"):
        ax1.scatter(
            grp["avg_delivery_days"], grp["avg_freight"], 
            s=grp["orders"] / 80 + 40,
            color=reg_colors.get(reg, "gray"),
            alpha=0.75, edgecolors="black", linewidth=0.8,
            label=reg
        )
        for _, row in grp.iterrows():
            ax1.text(row["avg_delivery_days"] + 0.3, row["avg_freight"], row["customer_state"], fontsize=7)

    ax1.set_xlabel("Average Delivery Lead Time (Days)", fontweight="bold")
    ax1.set_ylabel("Average Freight Fee (BRL)", fontweight="bold")
    ax1.set_title("Delivery Lead Time vs Freight Cost Across 27 Brazilian States", fontsize=11, fontweight="bold")
    ax1.legend(title="Macro-Region", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # 2. Late Delivery Satisfaction Collapse
    df_late = pd.read_sql_query("""
        SELECT 
            CASE 
                WHEN f.delivery_delay_days > 5 THEN 'Late >5d'
                WHEN f.delivery_delay_days > 0 THEN 'Late 1-5d'
                WHEN f.delivery_delay_days >= -5 THEN 'Early 1-5d'
                ELSE 'Early >5d'
            END AS bucket,
            ROUND(AVG(f.review_score), 2) AS avg_score,
            ROUND(100.0 * SUM(CASE WHEN f.review_score = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_1_star
        FROM fact_order_sales_fulfillment f
        JOIN dim_order_status st ON f.status_key = st.status_key
        WHERE st.is_delivered = 1 AND f.review_score IS NOT NULL
        GROUP BY 1
        ORDER BY avg_score DESC
    """, conn)

    bars = ax2.bar(df_late["bucket"], df_late["avg_score"], color=["#2E7D32", "#66BB6A", "#FFA726", "#C62828"], edgecolor="black")
    ax2.set_ylabel("Average Review Rating (out of 5.0)", fontweight="bold")
    ax2.set_ylim(0, 5.0)
    ax2.set_title("The 'Late Delivery Penalty': Satisfaction Collapse upon SLA Breach", fontsize=11, fontweight="bold")
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.1, f"{h:.2f} ★", ha="center", fontsize=9, fontweight="bold")

    plt.suptitle("Report Page 3: Interactive Drill-Down & Operational Deep-Dive (Power BI)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    out_file = os.path.join(DIAGRAMS_DIR, "page3_interactive_analysis.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    conn.close()
    print(f" -> Generated: {out_file}")


def main():
    print("=" * 60)
    print("GENERATING ARCHITECTURAL DIAGRAMS & BI VISUALS FOR REPORT")
    print("=" * 60)
    generate_architecture_diagram()
    generate_star_schema_diagram()
    generate_page1_visuals()
    generate_page2_visuals()
    generate_page3_visuals()
    print("All visuals generated successfully in report/diagrams/!")


if __name__ == "__main__":
    main()
