# -*- coding: utf-8 -*-
# Quick column profiling -> docs/profile_core.csv

import os, csv
import pandas as pd

PRJ = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW = os.path.join(PRJ, "data", "raw")
DOCS = os.path.join(PRJ, "docs")
os.makedirs(DOCS, exist_ok=True)

targets = {
    "olist_orders_dataset.csv":         os.path.join(RAW, "brazilian_ecommerce", "olist_orders_dataset.csv"),
    "olist_order_items_dataset.csv":    os.path.join(RAW, "brazilian_ecommerce", "olist_order_items_dataset.csv"),
    "olist_order_payments_dataset.csv": os.path.join(RAW, "brazilian_ecommerce", "olist_order_payments_dataset.csv"),
    "olist_order_reviews_dataset.csv":  os.path.join(RAW, "brazilian_ecommerce", "olist_order_reviews_dataset.csv"),
    "olist_customers_dataset.csv":      os.path.join(RAW, "brazilian_ecommerce", "olist_customers_dataset.csv"),
    "olist_products_dataset.csv":       os.path.join(RAW, "brazilian_ecommerce", "olist_products_dataset.csv"),
    "olist_sellers_dataset.csv":        os.path.join(RAW, "brazilian_ecommerce", "olist_sellers_dataset.csv"),
    "online_retail.csv":                os.path.join(RAW, "online_retail", "online_retail.csv"),
    "marketing_channels.csv":           os.path.join(RAW, "synthetic", "marketing_channels.csv"),
    "customer_service.csv":             os.path.join(RAW, "synthetic", "customer_service.csv"),
    "marketing_spend.csv":              os.path.join(RAW, "synthetic", "marketing_spend.csv"),
}

out_csv = os.path.join(DOCS, "profile_core.csv")
rows = []

for name, path in targets.items():
    if not os.path.exists(path):
        continue
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path, nrows=25000)
    else:
        df = pd.read_excel(path, nrows=25000)

    n = len(df)
    for c in df.columns:
        s = df[c]
        null_pct = round(float(s.isna().mean())*100, 2)
        try:
            uniq = int(s.nunique(dropna=True))
        except Exception:
            uniq = ""
        try:
            sample_vals = " | ".join(map(str, s.dropna().astype(str).unique()[:5]))
        except Exception:
            sample_vals = ""
        rows.append({
            "file": name,
            "column": c,
            "dtype": str(s.dtype),
            "rows_sampled": n,
            "null_pct": null_pct,
            "unique_n": uniq,
            "sample_values": sample_vals
        })

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["file","column","dtype","rows_sampled","null_pct","unique_n","sample_values"])
    w.writeheader()
    w.writerows(rows)

print("Wrote ->", out_csv)
