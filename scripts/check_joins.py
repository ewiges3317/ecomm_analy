# -*- coding: utf-8 -*-
# Join and key sanity -> docs/join_checks.txt

import os
import pandas as pd

PRJ = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW = os.path.join(PRJ, "data", "raw")
DOCS = os.path.join(PRJ, "docs")
os.makedirs(DOCS, exist_ok=True)
out_txt = os.path.join(DOCS, "join_checks.txt")

p_orders  = os.path.join(RAW, "brazilian_ecommerce", "olist_orders_dataset.csv")
p_items   = os.path.join(RAW, "brazilian_ecommerce", "olist_order_items_dataset.csv")
p_pay     = os.path.join(RAW, "brazilian_ecommerce", "olist_order_payments_dataset.csv")
p_cust    = os.path.join(RAW, "brazilian_ecommerce", "olist_customers_dataset.csv")
p_prod    = os.path.join(RAW, "brazilian_ecommerce", "olist_products_dataset.csv")
p_trans   = os.path.join(RAW, "brazilian_ecommerce", "product_category_name_translation.csv")

orders = pd.read_csv(p_orders, parse_dates=[
    "order_purchase_timestamp","order_approved_at",
    "order_delivered_carrier_date","order_delivered_customer_date",
    "order_estimated_delivery_date"
])
items  = pd.read_csv(p_items, parse_dates=["shipping_limit_date"])
pay    = pd.read_csv(p_pay)
cust   = pd.read_csv(p_cust)
prod   = pd.read_csv(p_prod)
trans  = pd.read_csv(p_trans)

lines = []

def dupe_report(df, cols, name):
    dupes = df.duplicated(subset=cols, keep=False).sum()
    lines.append(f"[{name}] duplicates on {cols}: {dupes}")

dupe_report(orders, ["order_id"], "orders")
dupe_report(items,  ["order_id","order_item_id"], "order_items")
dupe_report(pay,    ["order_id","payment_sequential"], "payments")
dupe_report(cust,   ["customer_id"], "customers")
dupe_report(prod,   ["product_id"], "products")

# Join order_items → (orders, payments agg, customers)
oi = items.merge(
    orders[["order_id","customer_id","order_status","order_purchase_timestamp"]],
    on="order_id", how="left"
)
oi_pay = pay.groupby("order_id", as_index=False)["payment_value"].sum().rename(columns={"payment_value":"order_payment_sum"})
oi = oi.merge(oi_pay, on="order_id", how="left")
oi = oi.merge(cust, on="customer_id", how="left")

# product category translation (for later dims)
prod2 = prod.merge(trans, on="product_category_name", how="left")

# Missing join rates
miss_orders = oi["order_status"].isna().mean()
miss_cust   = oi["customer_city"].isna().mean()
miss_pay    = oi["order_payment_sum"].isna().mean()

lines += [
    f"[join] items→orders missing rate: {miss_orders:.4f}",
    f"[join] items→customers missing rate: {miss_cust:.4f}",
    f"[join] items→payments (aggregated) missing rate: {miss_pay:.4f}",
]

# Payment sanity: compare item revenue vs payment_sum (rough)
oi["item_total"] = oi["price"] + oi["freight_value"]
rev_vs_pay = oi.groupby("order_id", as_index=False)[["item_total"]].sum().merge(oi_pay, on="order_id", how="left")
diff = (rev_vs_pay["order_payment_sum"] - rev_vs_pay["item_total"]).abs()
lines.append(f"[sanity] median |payment_sum - item_total|: {diff.median():.2f}")

# Output counts
lines.append(f"[counts] orders={len(orders)} items={len(items)} payments={len(pay)} customers={len(cust)} products={len(prod)}")

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Wrote ->", out_txt)
