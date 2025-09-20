# -*- coding: utf-8 -*-
import os, pandas as pd

PRJ = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW = os.path.join(PRJ, "data", "raw")
OUT = os.path.join(PRJ, "data", "processed", "base")
os.makedirs(OUT, exist_ok=True)

def parse_dates(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df

# ---- OLIST ----
orders = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_orders_dataset.csv"))
orders = parse_dates(orders, [
    "order_purchase_timestamp","order_approved_at",
    "order_delivered_carrier_date","order_delivered_customer_date",
    "order_estimated_delivery_date"
])
for c in ["order_status"]:
    orders[c] = orders[c].astype("category")
orders.to_csv(os.path.join(OUT,"olist_orders.csv"), index=False)

items = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_order_items_dataset.csv"))
items = parse_dates(items, ["shipping_limit_date"])
items.to_csv(os.path.join(OUT,"olist_order_items.csv"), index=False)

pay = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_order_payments_dataset.csv"))
pay["payment_type"] = pay["payment_type"].astype("category")
pay.to_csv(os.path.join(OUT,"olist_payments.csv"), index=False)

reviews = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_order_reviews_dataset.csv"))
reviews = parse_dates(reviews, ["review_creation_date","review_answer_timestamp"])
reviews.to_csv(os.path.join(OUT,"olist_reviews.csv"), index=False)

cust = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_customers_dataset.csv"))
cust["customer_state"] = cust["customer_state"].astype("category")
cust.to_csv(os.path.join(OUT,"olist_customers.csv"), index=False)

prod = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_products_dataset.csv"))
prod.to_csv(os.path.join(OUT,"olist_products.csv"), index=False)

sellers = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","olist_sellers_dataset.csv"))
sellers["seller_state"] = sellers["seller_state"].astype("category")
sellers.to_csv(os.path.join(OUT,"olist_sellers.csv"), index=False)

trans = pd.read_csv(os.path.join(RAW,"brazilian_ecommerce","product_category_name_translation.csv"))
trans.to_csv(os.path.join(OUT,"olist_category_translation.csv"), index=False)

# ---- Online Retail ----
ret_path = os.path.join(RAW,"online_retail","online_retail.csv")
if os.path.exists(ret_path):
    retail = pd.read_csv(ret_path)
    retail["InvoiceDate"] = pd.to_datetime(retail["InvoiceDate"], errors="coerce")
    retail["Country"] = retail["Country"].astype("category")
    retail.to_csv(os.path.join(OUT,"online_retail.csv"), index=False)

# ---- Synthetic ----
syn = os.path.join(RAW,"synthetic")
mc = os.path.join(syn,"marketing_channels.csv")
cs = os.path.join(syn,"customer_service.csv")
ms = os.path.join(syn,"marketing_spend.csv")

if os.path.exists(mc):
    df = pd.read_csv(mc)
    df["acquisition_date"] = pd.to_datetime(df["acquisition_date"], errors="coerce")
    for c in ["acquisition_channel","utm_source","utm_medium"]:
        df[c] = df[c].astype("category")
    df.to_csv(os.path.join(OUT,"marketing_channels.csv"), index=False)

if os.path.exists(cs):
    df = pd.read_csv(cs)
    for c in ["issue_date","resolution_date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df["issue_type"] = df["issue_type"].astype("category")
    df.to_csv(os.path.join(OUT,"customer_service.csv"), index=False)

if os.path.exists(ms):
    df = pd.read_csv(ms)
    df["month_year"] = pd.PeriodIndex(df["month_year"], freq="M").to_timestamp('M')
    df["channel"] = df["channel"].astype("category")
    df.to_csv(os.path.join(OUT,"marketing_spend.csv"), index=False)

print("Wrote normalized CSVs ->", OUT)
