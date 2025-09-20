import os, pandas as pd

PROJECT_ROOT = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
raw = os.path.join(PROJECT_ROOT, "data", "raw")

targets = [
    os.path.join(raw, "brazilian_ecommerce", "olist_orders_dataset.csv"),
    os.path.join(raw, "brazilian_ecommerce", "olist_order_items_dataset.csv"),
    os.path.join(raw, "brazilian_ecommerce", "olist_customers_dataset.csv"),
    os.path.join(raw, "brazilian_ecommerce", "olist_products_dataset.csv"),
    os.path.join(raw, "brazilian_ecommerce", "olist_order_payments_dataset.csv"),
    os.path.join(raw, "brazilian_ecommerce", "olist_order_reviews_dataset.csv"),
    os.path.join(raw, "online_retail", "online_retail.csv"),  # after conversion
    os.path.join(raw, "synthetic", "marketing_channels.csv"),
    os.path.join(raw, "synthetic", "customer_service.csv"),
    os.path.join(raw, "synthetic", "marketing_spend.csv"),
]

for p in targets:
    if not os.path.exists(p):
        print(f"[MISS] {p}")
        continue
    print("\n=== FILE:", os.path.relpath(p, PROJECT_ROOT))
    try:
        if p.lower().endswith(".csv"):
            df = pd.read_csv(p, nrows=5)
        else:
            df = pd.read_excel(p, nrows=5)
        print("columns:", list(df.columns))
        print(df.head(3).to_string(index=False))
    except Exception as e:
        print("error:", e)
