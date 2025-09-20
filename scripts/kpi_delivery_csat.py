import os
import pandas as pd
import numpy as np

BASE = r"data\processed\analysis"
OUTD = r"data\processed\analysis"
DOCS = r"docs"
os.makedirs(OUTD, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

# -------- Load journey (safe: fall back to CSV if parquet engine missing)
parq = os.path.join(BASE, "journey_delivery_csat_repeat.parquet")
csv  = os.path.join(BASE, "journey_delivery_csat_repeat.csv")
df = None
if os.path.exists(parq):
    try:
        df = pd.read_parquet(parq)
    except Exception:
        df = pd.read_csv(csv, low_memory=False)
else:
    df = pd.read_csv(csv, low_memory=False)

# Clean minimal fields
for col in ["review_score","delivery_delay_days","repeat_90d","is_late","price_total"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# -------- Delay buckets
def delay_bucket(d):
    if pd.isna(d): return "unk"
    if d <= -2: return "early_2d_or_more"
    if -1 <= d <= 0: return "on_time"
    if 1 <= d <= 3: return "late_1to3"
    if 4 <= d <= 7: return "late_4to7"
    return "late_8plus"

df["delay_bucket"] = df["delivery_delay_days"].apply(delay_bucket) if "delivery_delay_days" in df.columns else "unk"

# -------- KPI 1: Late% by state
if "customer_state" in df.columns and "is_late" in df.columns:
    kpi_late_state = (
        df.assign(cnt=1)
          .groupby("customer_state", dropna=False)
          .agg(orders=("cnt","sum"), late_orders=("is_late","sum"))
          .reset_index()
    )
    kpi_late_state["late_pct"] = (kpi_late_state["late_orders"] / kpi_late_state["orders"] * 100).round(2)
    kpi_late_state = kpi_late_state.sort_values("late_pct", ascending=False)
else:
    kpi_late_state = pd.DataFrame(columns=["customer_state","orders","late_orders","late_pct"])

# -------- KPI 2: Review by delay bucket
if "review_score" in df.columns:
    kpi_review_delay = (
        df.groupby("delay_bucket", dropna=False)["review_score"]
          .agg(n="count", avg_review="mean")
          .reset_index()
          .sort_values("avg_review", ascending=False)
    )
    kpi_review_delay["avg_review"] = kpi_review_delay["avg_review"].round(3)
else:
    kpi_review_delay = pd.DataFrame(columns=["delay_bucket","n","avg_review"])

# -------- KPI 3: Repeat within 90d by review bucket
if "review_score" in df.columns and "repeat_90d" in df.columns:
    df["review_star"] = df["review_score"].round().clip(lower=1, upper=5)
    kpi_repeat_by_review = (
        df.groupby("review_star", dropna=False)["repeat_90d"]
          .agg(n="count", repeat_rate=lambda s: s.mean()*100)
          .reset_index()
          .sort_values("review_star")
    )
    kpi_repeat_by_review["repeat_rate"] = kpi_repeat_by_review["repeat_rate"].round(2)
else:
    kpi_repeat_by_review = pd.DataFrame(columns=["review_star","n","repeat_rate"])

# -------- KPI 4: Repeat within 90d by late vs on-time
if "is_late" in df.columns and "repeat_90d" in df.columns:
    kpi_repeat_by_late = (
        df.groupby("is_late")["repeat_90d"]
          .agg(n="count", repeat_rate=lambda s: s.mean()*100)
          .reset_index()
          .replace({"is_late": {0: "on_time", 1: "late"}})
          .sort_values("repeat_rate", ascending=False)
    )
    kpi_repeat_by_late["repeat_rate"] = kpi_repeat_by_late["repeat_rate"].round(2)
else:
    kpi_repeat_by_late = pd.DataFrame(columns=["is_late","n","repeat_rate"])

# -------- AOV by late vs on-time (optional)
if "price_total" in df.columns and "is_late" in df.columns:
    kpi_aov_by_late = (
        df.groupby("is_late")["price_total"]
          .agg(n="count", aov="mean")
          .reset_index()
          .replace({"is_late": {0: "on_time", 1: "late"}})
    )
    kpi_aov_by_late["aov"] = kpi_aov_by_late["aov"].round(2)
else:
    kpi_aov_by_late = pd.DataFrame(columns=["is_late","n","aov"])

# -------- Exec snapshot text
avg_rev_on  = df.loc[df.get("is_late",0)==0, "review_score"].mean() if "review_score" in df.columns else float("nan")
avg_rev_late= df.loc[df.get("is_late",1)==1, "review_score"].mean() if "review_score" in df.columns else float("nan")
rep_on      = df.loc[df.get("is_late",0)==0, "repeat_90d"].mean()*100 if "repeat_90d" in df.columns else float("nan")
rep_late    = df.loc[df.get("is_late",1)==1, "repeat_90d"].mean()*100 if "repeat_90d" in df.columns else float("nan")

lines = []
lines.append("=== DELIVERY → CSAT → REPEAT: SNAPSHOT ===")
lines.append(f"Orders analyzed: {len(df):,}")
if "is_late" in df.columns:
    lines.append(f"Late% overall: {df['is_late'].mean()*100:.2f}%")
if "review_score" in df.columns:
    lines.append(f"Avg review (on-time): {avg_rev_on:.2f} | (late): {avg_rev_late:.2f}")
if "repeat_90d" in df.columns:
    lines.append(f"Repeat 90d (on-time): {rep_on:.2f}% | (late): {rep_late:.2f}%")
if not kpi_late_state.empty:
    lines.append("")
    lines.append("Top states by late% (first 10):")
    head = kpi_late_state.head(10)[["customer_state","orders","late_pct"]]
    for _,r in head.iterrows():
        lines.append(f"- {r['customer_state']}: {r['late_pct']:.2f}% late (n={int(r['orders'])})")

with open(os.path.join(DOCS, "exec_snapshot_delivery_csat_repeat.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

# -------- Save CSVs
kpi_late_state.to_csv(os.path.join(OUTD, "kpi_late_by_state.csv"), index=False)
kpi_review_delay.to_csv(os.path.join(OUTD, "kpi_review_by_delay_bucket.csv"), index=False)
kpi_repeat_by_review.to_csv(os.path.join(OUTD, "kpi_repeat_by_review_star.csv"), index=False)
kpi_repeat_by_late.to_csv(os.path.join(OUTD, "kpi_repeat_by_late.csv"), index=False)
kpi_aov_by_late.to_csv(os.path.join(OUTD, "kpi_aov_by_late.csv"), index=False)

print("Wrote KPIs + snapshot (parquet optional; CSV fallback used if needed)")
