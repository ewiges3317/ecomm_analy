# -*- coding: utf-8 -*-
# Prints quick distributions / sanity KPIs to console

import os, pandas as pd, numpy as np

PRJ = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW = os.path.join(PRJ, "data", "raw")

p_orders = os.path.join(RAW, "brazilian_ecommerce", "olist_orders_dataset.csv")
p_pay    = os.path.join(RAW, "brazilian_ecommerce", "olist_order_payments_dataset.csv")
p_items  = os.path.join(RAW, "brazilian_ecommerce", "olist_order_items_dataset.csv")
p_retail = os.path.join(RAW, "online_retail", "online_retail.csv")

print("\n=== OLIST: order_status distribution ===")
orders = pd.read_csv(p_orders)
print(orders["order_status"].value_counts(dropna=False).to_string())

print("\n=== OLIST: payment_type mix ===")
pay = pd.read_csv(p_pay)
print(pay["payment_type"].value_counts(dropna=False).to_string())

print("\n=== OLIST: basic price/freight sanity ===")
items = pd.read_csv(p_items, usecols=["price","freight_value"])
neg_price = (items["price"]<0).sum()
neg_freight = (items["freight_value"]<0).sum()
zero_price = (items["price"]==0).sum()
print(f"rows: {len(items)} | neg_price: {neg_price} | zero_price: {zero_price} | neg_freight: {neg_freight}")

print("\n=== ONLINE RETAIL: returns & missing customers ===")
ret = pd.read_csv(p_retail, parse_dates=["InvoiceDate"])
returns = (ret["Quantity"]<0).sum()
missing_cust = ret["CustomerID"].isna().mean()*100
print(f"rows: {len(ret)} | returns(rows with Quantity<0): {returns} | missing CustomerID %%: {missing_cust:.2f}")

print("\n=== ONLINE RETAIL: date range ===")
print(ret["InvoiceDate"].min(), "→", ret["InvoiceDate"].max())
