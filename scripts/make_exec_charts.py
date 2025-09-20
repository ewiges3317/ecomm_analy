import os
import pandas as pd
import matplotlib.pyplot as plt

BASE = r"data\processed\analysis"
DOCS = r"docs"
OUTP = r"outputs\dashboards"
os.makedirs(OUTP, exist_ok=True)

# --- Load journey (parquet optional; CSV fallback)
parq = os.path.join(BASE, "journey_delivery_csat_repeat.parquet")
csv  = os.path.join(BASE, "journey_delivery_csat_repeat.csv")
if os.path.exists(parq):
    try:
        df = pd.read_parquet(parq)
    except Exception:
        df = pd.read_csv(csv, low_memory=False)
else:
    df = pd.read_csv(csv, low_memory=False)

# Basic cleaning
for c in ["is_late","review_score","repeat_90d","delivery_delay_days"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# 1) Late% by state (Top 15 by orders)
out1 = None
if "customer_state" in df.columns and "is_late" in df.columns:
    state = (
        df.assign(one=1)
          .groupby("customer_state", dropna=False)
          .agg(orders=("one","sum"), late=("is_late","mean"))
          .reset_index()
          .sort_values("orders", ascending=False)
          .head(15)
    )
    state["late_pct"] = state["late"] * 100
    plt.figure()
    plt.bar(state["customer_state"], state["late_pct"])
    plt.title("Late Deliveries (%) — Top Volume States")
    plt.xlabel("State")
    plt.ylabel("Late %")
    plt.tight_layout()
    out1 = os.path.join(OUTP, "late_pct_by_state_top.png")
    plt.savefig(out1, dpi=160)
    plt.close()

# 2) Avg review by delay bucket
def delay_bucket(d):
    if pd.isna(d):  return "unknown"
    if d <= -2:     return "early_2d_plus"
    if -1 <= d <= 0:return "on_time"
    if 1 <= d <= 3: return "late_1to3"
    if 4 <= d <= 7: return "late_4to7"
    return "late_8plus"

out2 = None
if "delivery_delay_days" in df.columns and "review_score" in df.columns:
    tmp = df.copy()
    tmp["delay_bucket"] = tmp["delivery_delay_days"].apply(delay_bucket)
    buck = (tmp.groupby("delay_bucket")["review_score"]
              .agg(avg_review="mean", n="count")
              .reset_index())
    order = ["early_2d_plus","on_time","late_1to3","late_4to7","late_8plus","unknown"]
    buck["order"] = buck["delay_bucket"].map({k:i for i,k in enumerate(order)})
    buck = buck.sort_values("order")
    plt.figure()
    plt.bar(buck["delay_bucket"], buck["avg_review"])
    plt.title("Average Review by Delivery Delay Bucket")
    plt.xlabel("Delay Bucket")
    plt.ylabel("Average Review")
    plt.xticks(rotation=20)
    plt.tight_layout()
    out2 = os.path.join(OUTP, "avg_review_by_delay_bucket.png")
    plt.savefig(out2, dpi=160)
    plt.close()

# 3) Repeat within 90d — On-time vs Late
out3 = None
if "is_late" in df.columns and "repeat_90d" in df.columns:
    rep = (df.groupby("is_late")["repeat_90d"].mean().reset_index()
             .replace({"is_late": {0:"on_time", 1:"late"}}))
    rep["repeat_pct"] = rep["repeat_90d"] * 100
    plt.figure()
    plt.bar(rep["is_late"], rep["repeat_pct"])
    plt.title("Repeat within 90 Days")
    plt.xlabel("Segment")
    plt.ylabel("Repeat %")
    plt.tight_layout()
    out3 = os.path.join(OUTP, "repeat_90d_on_time_vs_late.png")
    plt.savefig(out3, dpi=160)
    plt.close()

# Write a tiny readme with paths
with open(os.path.join(DOCS, "EXEC_CHARTS_README.txt"), "w", encoding="utf-8") as f:
    f.write("Charts saved:\n")
    for p in [out1, out2, out3]:
        if p: f.write(f"- {p}\n")

print("Saved charts:")
for p in [out1, out2, out3]:
    if p: print(" ", p)
print("Wrote docs\\EXEC_CHARTS_README.txt")
