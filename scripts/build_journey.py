import os
import pandas as pd

BASE = r"data\processed\base"
OUTDIR = r"data\processed\analysis"
os.makedirs(OUTDIR, exist_ok=True)

# Load required tables
orders  = pd.read_csv(os.path.join(BASE, "olist_orders.csv"), low_memory=False)
items   = pd.read_csv(os.path.join(BASE, "olist_order_items.csv"), low_memory=False)
reviews = pd.read_csv(os.path.join(BASE, "olist_reviews.csv"), low_memory=False)
cust    = pd.read_csv(os.path.join(BASE, "olist_customers.csv"), low_memory=False)
sellers = pd.read_csv(os.path.join(BASE, "olist_sellers.csv"), low_memory=False)

# Optional enrich
try:
    products = pd.read_csv(os.path.join(BASE, "olist_products.csv"), low_memory=False)
except FileNotFoundError:
    products = pd.DataFrame()

# Parse timestamps
to_dt = lambda s: pd.to_datetime(s, errors="coerce")
orders["order_purchase_timestamp"]      = to_dt(orders.get("order_purchase_timestamp"))
orders["order_delivered_customer_date"] = to_dt(orders.get("order_delivered_customer_date"))
orders["order_estimated_delivery_date"] = to_dt(orders.get("order_estimated_delivery_date"))

# Delivery metrics
orders["delivery_delay_days"] = (
    (orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]).dt.days
)
orders["delivery_delay_days"] = orders["delivery_delay_days"].fillna(0)
orders["is_late"] = (orders["delivery_delay_days"] > 0).astype("int8")

# Order-level price/freight & seller_count
agg_items = items.groupby("order_id", as_index=False).agg(
    item_count=("order_item_id", "count"),
    price_total=("price", "sum"),
    freight_total=("freight_value", "sum"),
    seller_count=("seller_id", "nunique")
)

# Take latest review per order if duplicates
if "review_creation_date" in reviews.columns:
    reviews["review_creation_date"] = to_dt(reviews["review_creation_date"])
    reviews = (
        reviews.sort_values(["order_id","review_creation_date"])
               .groupby("order_id", as_index=False)
               .tail(1)
    )
else:
    reviews = reviews.drop_duplicates("order_id", keep="last")

# Base journey
journey = (
    orders.merge(agg_items, on="order_id", how="left")
          .merge(reviews[["order_id","review_score"]], on="order_id", how="left")
          .merge(cust[["customer_id","customer_unique_id","customer_city","customer_state"]], on="customer_id", how="left")
)

# First seller per order for seller geo
first_seller = (
    items.sort_values(["order_id","order_item_id"])
         .groupby("order_id", as_index=False)
         .first()[["order_id","seller_id"]]
)
journey = journey.merge(first_seller, on="order_id", how="left")
journey = journey.merge(sellers[["seller_id","seller_city","seller_state"]], on="seller_id", how="left")

# Optional first product dims
if not products.empty:
    first_prod = (
        items.sort_values(["order_id","order_item_id"])
             .groupby("order_id", as_index=False)
             .first()[["order_id","product_id"]]
    )
    pcols = [c for c in ["product_id","product_weight_g","product_length_cm","product_height_cm","product_width_cm"]
             if c in products.columns]
    journey = journey.merge(first_prod, on="order_id", how="left")
    if pcols:
        journey = journey.merge(products[pcols], on="product_id", how="left")

# Repeat within 90 days (next order of same customer_unique_id)
journey = journey.sort_values(["customer_unique_id","order_purchase_timestamp"])
journey["next_purchase_ts"] = journey.groupby("customer_unique_id")["order_purchase_timestamp"].shift(-1)
journey["repeat_90d"] = (
    (journey["next_purchase_ts"].notna()) &
    ((journey["next_purchase_ts"] - journey["order_purchase_timestamp"]) <= pd.Timedelta(days=90))
).astype("int8")

# Keep tidy subset
keep = [
    "order_id","customer_id","customer_unique_id",
    "order_purchase_timestamp",
    "order_delivered_customer_date","order_estimated_delivery_date",
    "delivery_delay_days","is_late","review_score",
    "item_count","price_total","freight_total","seller_count",
    "customer_city","customer_state","seller_id","seller_city","seller_state",
    "product_id","product_weight_g","product_length_cm","product_height_cm","product_width_cm",
    "repeat_90d"
]
keep = [c for c in keep if c in journey.columns]
journey_out = journey[keep].copy()

# Write
csv_path = os.path.join(OUTDIR, "journey_delivery_csat_repeat.csv")
par_path = os.path.join(OUTDIR, "journey_delivery_csat_repeat.parquet")
journey_out.to_csv(csv_path, index=False)

wrote_parquet = False
try:
    import pyarrow as pa, pyarrow.parquet as pq
    journey_out.to_parquet(par_path, index=False)
    wrote_parquet = True
except Exception:
    pass

print(f"Wrote: {csv_path}")
print(f"Wrote parquet: {wrote_parquet} -> {par_path if wrote_parquet else '(pyarrow not installed)'}")
print(f"Rows: {len(journey_out):,} | Late%: {journey_out['is_late'].mean()*100:.2f} | Avg review: {journey_out['review_score'].mean():.2f}")
