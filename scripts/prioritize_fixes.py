import os
import pandas as pd
import numpy as np

BASE = r"data\processed\analysis"
OUTD = BASE
DOCS = r"docs"
os.makedirs(OUTD, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

MIN_STATE_ORDERS = 200
MIN_SELLER_ORDERS = 100
TARGET_LATE_REDUCTION_PP_STATE = 3.0
TARGET_LATE_REDUCTION_REL_SELLER = 0.20
HIGH_LATE_SELLER_PCT = 0.10

# Load journey (parquet optional; CSV fallback)
parq = os.path.join(BASE, "journey_delivery_csat_repeat.parquet")
csv  = os.path.join(BASE, "journey_delivery_csat_repeat.csv")
if os.path.exists(parq):
    try:
        df = pd.read_parquet(parq)
    except Exception:
        df = pd.read_csv(csv, low_memory=False)
else:
    df = pd.read_csv(csv, low_memory=False)

for c in ["is_late","repeat_90d","price_total","customer_state","seller_id"]:
    if c not in df.columns:
        if c in ("customer_state","seller_id"): df[c] = "UNK"
        elif c == "price_total": df[c] = np.nan
        else: df[c] = 0

df["is_late"] = pd.to_numeric(df["is_late"], errors="coerce").fillna(0).astype(int)
df["repeat_90d"] = pd.to_numeric(df["repeat_90d"], errors="coerce").fillna(0).astype(int)
df["price_total"] = pd.to_numeric(df["price_total"], errors="coerce")

on_rep = df.loc[df["is_late"]==0, "repeat_90d"].mean() * 100.0
lt_rep = df.loc[df["is_late"]==1, "repeat_90d"].mean() * 100.0
delta_repeat_pp = max(on_rep - lt_rep, 0.0)
delta_repeat = delta_repeat_pp / 100.0
AOV = float(df["price_total"].mean()) if df["price_total"].notna().any() else 137.75

# ----- STATE RANK -----
state = (df.assign(one=1)
           .groupby("customer_state", dropna=False)
           .agg(orders=("one","sum"), late_orders=("is_late","sum"), aov=("price_total","mean"))
           .reset_index())
state["late_pct"] = (state["late_orders"]/state["orders"]*100.0)
state["aov"] = state["aov"].fillna(AOV)

def sim_state(r):
    if r["orders"] < MIN_STATE_ORDERS:
        return pd.Series({"convert_orders": 0, "inc_repeats": 0.0, "inc_revenue": 0.0})
    current_pp = r["late_pct"]
    target_pp  = max(current_pp - TARGET_LATE_REDUCTION_PP_STATE, 0.0)
    target_late_orders = int(round(r["orders"] * (target_pp/100.0)))
    convert_orders = max(int(r["late_orders"]) - target_late_orders, 0)
    inc_repeats = convert_orders * delta_repeat
    inc_revenue = inc_repeats * r["aov"]
    return pd.Series({"convert_orders": convert_orders, "inc_repeats": inc_repeats, "inc_revenue": inc_revenue})

state_out = pd.concat([state, state.apply(sim_state, axis=1)], axis=1).sort_values("inc_revenue", ascending=False)
state_out.to_csv(os.path.join(OUTD, "prioritize_states.csv"), index=False)

# ----- SELLER RANK -----
seller = (df.assign(one=1)
            .groupby("seller_id", dropna=False)
            .agg(orders=("one","sum"), late_orders=("is_late","sum"), aov=("price_total","mean"))
            .reset_index())
seller["late_pct"] = (seller["late_orders"]/seller["orders"]*100.0)
seller["aov"] = seller["aov"].fillna(AOV)

def sim_seller(r):
    if r["orders"] < MIN_SELLER_ORDERS: return pd.Series({"convert_orders": 0, "inc_repeats": 0.0, "inc_revenue": 0.0})
    if r["late_pct"] < HIGH_LATE_SELLER_PCT*100: return pd.Series({"convert_orders": 0, "inc_repeats": 0.0, "inc_revenue": 0.0})
    convert_orders = int(round(r["late_orders"] * TARGET_LATE_REDUCTION_REL_SELLER))
    inc_repeats = convert_orders * delta_repeat
    inc_revenue = inc_repeats * r["aov"]
    return pd.Series({"convert_orders": convert_orders, "inc_repeats": inc_repeats, "inc_revenue": inc_revenue})

seller_out = pd.concat([seller, seller.apply(sim_seller, axis=1)], axis=1).sort_values("inc_revenue", ascending=False)
seller_out.to_csv(os.path.join(OUTD, "prioritize_sellers.csv"), index=False)

# ----- SELLER x STATE MATRIX -----
sx = (df.assign(one=1)
        .groupby(["customer_state","seller_id"], dropna=False)
        .agg(orders=("one","sum"), late_orders=("is_late","sum"))
        .reset_index())
sx["late_pct"] = (sx["late_orders"]/sx["orders"]*100.0)
sx = sx[sx["orders"] >= 50].sort_values(["late_pct","orders"], ascending=[False, False])
sx.to_csv(os.path.join(OUTD, "seller_by_state_matrix.csv"), index=False)

# ----- TEXT SUMMARY -----
lines = []
lines.append("=== WHERE TO FIX FIRST — PRIORITIZATION ===")
lines.append(f"Lift assumption: converting late → on-time yields +{delta_repeat_pp:.2f} pp to repeat-in-90d")
lines.append(f"Assumed AOV: ${AOV:,.2f}")
lines.append("")
lines.append(f"Top states by $ impact (simulate -{TARGET_LATE_REDUCTION_PP_STATE:.0f} pp late):")
for _, r in state_out.head(10)[["customer_state","orders","late_pct","convert_orders","inc_revenue"]].iterrows():
    lines.append(f"- {r['customer_state']}: {int(r['orders']):,} orders, late {r['late_pct']:.1f}% → convert {int(r['convert_orders']):,} → +${r['inc_revenue']:,.0f}")
lines.append("")
lines.append(f"Top sellers by $ impact (≥{MIN_SELLER_ORDERS} orders & late% ≥ {HIGH_LATE_SELLER_PCT*100:.0f}%):")
for _, r in seller_out.head(10)[["seller_id","orders","late_pct","convert_orders","inc_revenue"]].iterrows():
    lines.append(f"- {r['seller_id']}: {int(r['orders']):,} orders, late {r['late_pct']:.1f}% → convert {int(r['convert_orders']):,} → +${r['inc_revenue']:,.0f}")

with open(os.path.join(DOCS, "prioritize_fixes_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Wrote:")
print(" - data\\processed\\analysis\\prioritize_states.csv")
print(" - data\\processed\\analysis\\prioritize_sellers.csv")
print(" - data\\processed\\analysis\\seller_by_state_matrix.csv")
print(" - docs\\prioritize_fixes_summary.txt")
