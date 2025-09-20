# -*- coding: utf-8 -*-
# Basic DQ/outliers -> docs/quality_flags.txt

import os, numpy as np, pandas as pd

PRJ = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW = os.path.join(PRJ,"data","raw")
DOCS = os.path.join(PRJ,"docs")
BASE = os.path.join(PRJ,"data","processed","base")
os.makedirs(DOCS, exist_ok=True)
outp = os.path.join(DOCS,"quality_flags.txt")

lines = []

# 1) Olist: products with zero/insane dimensions or weight
prod = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_products_dataset.csv"))
bad_dims = (
    (prod["product_weight_g"]<=0) |
    (prod["product_length_cm"]<=0) |
    (prod["product_height_cm"]<=0) |
    (prod["product_width_cm"]<=0)
).sum()
lines.append(f"[products] non-positive dimension/weight rows: {int(bad_dims)}")

# 2) Olist: orders delivered after estimated date?
orders = pd.read_csv(os.path.join(BASE,"olist_orders.csv"), parse_dates=[
    "order_delivered_customer_date","order_estimated_delivery_date"
])
late = (orders["order_delivered_customer_date"]>orders["order_estimated_delivery_date"]).sum()
lines.append(f"[orders] delivered AFTER estimate: {int(late)}")

# 3) Online Retail: negative prices or absurd quantities
ret = os.path.join(BASE,"online_retail.csv")
if os.path.exists(ret):
    df = pd.read_csv(ret, parse_dates=["InvoiceDate"])
    neg_qty = (df["Quantity"]<0).sum()
    zero_or_neg_price = (df["UnitPrice"]<=0).sum()
    lines.append(f"[online_retail] returns rows (Quantity<0): {int(neg_qty)}")
    lines.append(f"[online_retail] zero/neg UnitPrice rows: {int(zero_or_neg_price)}")

# 4) Payments vs items: median absolute diff check (same as join sanity, summarized)
items = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_order_items_dataset.csv"))
pay   = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_order_payments_dataset.csv"))
items["item_total"] = items["price"] + items["freight_value"]
rev_vs_pay = items.groupby("order_id", as_index=False)["item_total"].sum().merge(
    pay.groupby("order_id", as_index=False)["payment_value"].sum().rename(columns={"payment_value":"order_payment_sum"}),
    on="order_id", how="left"
)
diff = (rev_vs_pay["order_payment_sum"] - rev_vs_pay["item_total"]).abs()
lines.append(f"[payments] median |payment_sum - item_total|: {diff.median():.2f}")

with open(outp,"w",encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Wrote ->", outp)
