import os, glob, csv
import pandas as pd

BASE = r"data\processed\base"
OUT  = r"docs\delivery_inputs_inventory.csv"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def row_count_fast(path):
    # Robust line count for CSV; subtract header
    with open(path, 'rb') as f:
        return sum(1 for _ in f) - 1

files = sorted(glob.glob(os.path.join(BASE, "*.csv")))
signals = [
    "order_id","customer_id","seller_id",
    "order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date",
    "review_score","review_comment_message",
    "product_id","product_weight_g","product_length_cm","product_height_cm","product_width_cm",
    "geolocation_lat","geolocation_lng","customer_city","customer_state","seller_city","seller_state",
    "freight_value","price","payment_type"
]

rows = []
for fp in files:
    try:
        sample = pd.read_csv(fp, nrows=50, low_memory=False)
        cols = [c.strip() for c in sample.columns]
        hit = [s for s in signals if s in cols]
        rows.append({
            "file": os.path.basename(fp),
            "rows_est": row_count_fast(fp),
            "cols": len(cols),
            "key_signals_found": ";".join(hit)
        })
    except Exception as e:
        rows.append({"file": os.path.basename(fp), "rows_est": -1, "cols": -1, "key_signals_found": f"ERROR: {e}"})

pd.DataFrame(rows).to_csv(OUT, index=False, quoting=csv.QUOTE_MINIMAL)
print(f"Wrote manifest -> {OUT}")
