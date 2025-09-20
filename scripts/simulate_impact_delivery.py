import os
import pandas as pd
import numpy as np

# ====== TUNABLE PARAMETERS ======
REDUCE_LATE_PP_OVERALL = 5.0
REDUCE_LATE_PP_BY_STATE = 3.0
MIN_STATE_ORDERS = 200
REPEAT_WINDOW_DAYS = 90

BASE = r"data\processed\analysis"
DOCS = r"docs"
OUTD = r"data\processed\analysis"
os.makedirs(DOCS, exist_ok=True)
os.makedirs(OUTD, exist_ok=True)

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

# Ensure fields
for c in ["is_late","repeat_90d","price_total","customer_state"]:
    if c not in df.columns:
        if c == "price_total":
            df[c] = np.nan
        elif c == "customer_state":
            df[c] = "UNK"
        else:
            df[c] = 0

df["is_late"] = pd.to_numeric(df["is_late"], errors="coerce").fillna(0).astype(int)
df["repeat_90d"] = pd.to_numeric(df["repeat_90d"], errors="coerce").fillna(0).astype(int)
df["price_total"] = pd.to_numeric(df["price_total"], errors="coerce")

# --- Baselines
N = len(df)
late_rate = df["is_late"].mean() * 100.0
on_rep = df.loc[df["is_late"] == 0, "repeat_90d"].mean() * 100.0
lt_rep = df.loc[df["is_late"] == 1, "repeat_90d"].mean() * 100.0
delta_repeat_rate_pp = max(on_rep - lt_rep, 0.0)
delta_repeat_rate = delta_repeat_rate_pp / 100.0

AOV_overall = float(df["price_total"].mean()) if df["price_total"].notna().any() else 137.75

def inc_repeats_from_convert(k):
    return k * delta_repeat_rate

# Overall scenario
target_late_pp = max(late_rate - REDUCE_LATE_PP_OVERALL, 0.0)
current_late_orders = int(round(N * (late_rate/100.0)))
target_late_orders = int(round(N * (target_late_pp/100.0)))
convert_overall = max(current_late_orders - target_late_orders, 0)

inc_repeats_overall = inc_repeats_from_convert(convert_overall)
inc_revenue_overall = inc_repeats_overall * AOV_overall

# State-level scenario
by_state = (
    df.assign(one=1)
      .groupby("customer_state", dropna=False)
      .agg(orders=("one","sum"), late_orders=("is_late","sum"), aov=("price_total","mean"))
      .reset_index()
)
by_state["late_pct"] = (by_state["late_orders"]/by_state["orders"]*100.0)
by_state["aov"] = by_state["aov"].fillna(AOV_overall)

def calc_state_row(r):
    orders = int(r["orders"]); late_orders = int(r["late_orders"])
    if orders < MIN_STATE_ORDERS:
        return pd.Series({"target_late_pp": np.nan, "convert_orders": 0, "inc_repeats": 0.0, "inc_revenue": 0.0})
    current_pp = (late_orders / max(orders,1)) * 100.0
    target_pp  = max(current_pp - REDUCE_LATE_PP_BY_STATE, 0.0)
    target_late_orders = int(round(orders * (target_pp/100.0)))
    convert_orders = max(late_orders - target_late_orders, 0)
    inc_repeats = inc_repeats_from_convert(convert_orders)
    inc_revenue = inc_repeats * float(r["aov"])
    return pd.Series({"target_late_pp": target_pp, "convert_orders": convert_orders,
                      "inc_repeats": inc_repeats, "inc_revenue": inc_revenue})

impact_state = pd.concat([by_state, by_state.apply(calc_state_row, axis=1)], axis=1)
impact_state = impact_state.sort_values("inc_revenue", ascending=False)

impact_csv = os.path.join(OUTD, "impact_by_state.csv")
impact_state.to_csv(impact_csv, index=False)

lines = []
lines.append("=== DELIVERY → CSAT → REPEAT: $ IMPACT SIMULATION ===")
lines.append(f"Orders analyzed: {N:,}")
lines.append(f"Baseline late%: {late_rate:.2f}%")
lines.append(f"Observed repeat 90d: on-time {on_rep:.2f}% | late {lt_rep:.2f}%")
lines.append(f"Delta repeat rate from fixing lateness: +{delta_repeat_rate_pp:.2f} pp")
lines.append(f"Assumed AOV: ${AOV_overall:,.2f}")
lines.append("")
lines.append(f"[Overall] Reduce late% by {REDUCE_LATE_PP_OVERALL:.1f} pp:")
lines.append(f"- Late orders converted: {convert_overall:,}")
lines.append(f"- Incremental repeat orders: {inc_repeats_overall:,.0f}")
lines.append(f"- Incremental revenue: ${inc_revenue_overall:,.2f}")
lines.append("")
lines.append(f"[By State] Reduce late% by {REDUCE_LATE_PP_BY_STATE:.1f} pp per state (>= {MIN_STATE_ORDERS} orders):")
for _, r in impact_state.head(10)[["customer_state","orders","late_pct","convert_orders","inc_repeats","inc_revenue"]].iterrows():
    lines.append(f"- {r['customer_state']}: convert {int(r['convert_orders']):,} late → +{int(round(r['inc_repeats'])):,} repeats → +${float(r['inc_revenue']):,.0f}")

with open(os.path.join(DOCS, "impact_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Wrote impact files:")
print(f" - {impact_csv}")
print(" - docs\\impact_summary.txt")
