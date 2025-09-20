# scripts/make_sample_data.py
from pathlib import Path
import pandas as pd
from scripts._paths import RAW_BRAZIL

RAW_BRAZIL.mkdir(parents=True, exist_ok=True)

orders = pd.DataFrame({
    "order_id": ["o1","o2","o3"],
    "customer_id": ["c1","c1","c2"],
    "order_purchase_timestamp": pd.to_datetime(["2021-01-01","2021-01-10","2021-02-01"]),
    "order_delivered_customer_date": pd.to_datetime(["2021-01-05","2021-01-15","2021-02-05"]),
    "order_estimated_delivery_date": pd.to_datetime(["2021-01-04","2021-01-12","2021-02-03"]),
})
orders.to_csv(RAW_BRAZIL/"olist_orders_dataset.csv", index=False)

items = pd.DataFrame({
    "order_id": ["o1","o2","o3"],
    "order_item_id": [1,1,1],
    "product_id": ["p1","p2","p1"],
    "seller_id": ["s1","s2","s1"],
    "price": [100,200,150],
    "freight_value": [10,20,15],
    "shipping_limit_date": pd.to_datetime(["2021-01-02","2021-01-12","2021-02-02"]),
})
items.to_csv(RAW_BRAZIL/"olist_order_items_dataset.csv", index=False)

reviews = pd.DataFrame({
    "review_id": ["r1","r2","r3"],
    "order_id": ["o1","o2","o3"],
    "review_score": [5,3,4],
    "review_creation_date": pd.to_datetime(["2021-01-06","2021-01-16","2021-02-06"]),
})
reviews.to_csv(RAW_BRAZIL/"olist_order_reviews_dataset.csv", index=False)

customers = pd.DataFrame({
    "customer_id": ["c1","c2"],
    "customer_unique_id": ["u1","u2"],
    "customer_city": ["city1","city2"],
    "customer_state": ["ST1","ST2"],
})
customers.to_csv(RAW_BRAZIL/"olist_customers_dataset.csv", index=False)

sellers = pd.DataFrame({
    "seller_id": ["s1","s2"],
    "seller_city": ["sc1","sc2"],
    "seller_state": ["SS1","SS2"],
})
sellers.to_csv(RAW_BRAZIL/"olist_sellers_dataset.csv", index=False)

products = pd.DataFrame({
    "product_id": ["p1","p2"],
    "product_weight_g": [500,1000],
    "product_length_cm": [20,30],
    "product_height_cm": [10,15],
    "product_width_cm": [5,8],
})
products.to_csv(RAW_BRAZIL/"olist_products_dataset.csv", index=False)

print("Sample data written to", RAW_BRAZIL)
