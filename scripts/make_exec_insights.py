import os, pandas as pd

BASE = r"data\processed\analysis"
DOCS = r"docs"
os.makedirs(DOCS, exist_ok=True)

journey_csv = os.path.join(BASE, "journey_delivery_csat_repeat.csv")
kpi_state   = os.path.join(BASE, "kpi_late_by_state.csv")
kpi_delay   = os.path.join(BASE, "kpi_review_by_delay_bucket.csv")
prio_txt    = os.path.join(DOCS, "prioritize_fixes_summary.txt")
impact_txt  = os.path.join(DOCS, "impact_summary.txt")

out_md = os.path.join(DOCS, "EXEC_Insights_Delivery_CSAT_Repeat.md")

df = pd.read_csv(journey_csv, low_memory=False)

orders = len(df)
late_pct = pd.to_numeric(df["is_late"], errors="coerce").mean()*100
avg_rev_on  = pd.to_numeric(df["review_score"], errors="coerce")[df["is_late"]==0].mean()
avg_rev_lt  = pd.to_numeric(df["review_score"], errors="coerce")[df["is_late"]==1].mean()
rep_on      = pd.to_numeric(df["repeat_90d"], errors="coerce")[df["is_late"]==0].mean()*100
rep_lt      = pd.to_numeric(df["repeat_90d"], errors="coerce")[df["is_late"]==1].mean()*100
aov = pd.to_numeric(df.get("price_total", pd.Series(dtype=float)), errors="coerce").dropna().mean()
if pd.isna(aov): aov = 137.75

def read_txt(p):
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f: return f.read().strip()
    return "(summary not yet generated)"

st = pd.read_csv(kpi_state) if os.path.exists(kpi_state) else pd.DataFrame()
dl = pd.read_csv(kpi_delay) if os.path.exists(kpi_delay) else pd.DataFrame()

lines = []
lines.append("# Delivery → CSAT → Repeat — Executive Insights")
lines.append("")
lines.append("## Headline")
lines.append(f"- **Orders analyzed:** {orders:,}")
lines.append(f"- **Late deliveries:** {late_pct:.2f}%")
lines.append(f"- **Avg review:** on-time {avg_rev_on:.2f} vs late {avg_rev_lt:.2f}")
lines.append(f"- **Repeat in 90d:** on-time {rep_on:.2f}% vs late {rep_lt:.2f}%")
lines.append(f"- **Assumed AOV:** ${aov:,.2f}")
lines.append("")
lines.append("## What’s driving impact")
if not dl.empty and "delay_bucket" in dl and "avg_review" in dl:
    dl_sorted = dl.sort_values("avg_review", ascending=False)
    top = dl_sorted.head(5)
    for _, r in top.iterrows():
        lines.append(f"- **{r['delay_bucket']}** → avg review **{r['avg_review']:.2f}** (n={int(r['n'])})")
else:
    lines.append("- Delay bucket table not available.")
lines.append("")
lines.append("## Where to fix first (top states by lateness)")
if not st.empty:
    top_states = st.sort_values("late_pct", ascending=False).head(10)
    for _, r in top_states.iterrows():
        lines.append(f"- {r['customer_state']}: {r['late_pct']:.2f}% late (n={int(r['orders'])})")
else:
    lines.append("- State KPI not available.")
lines.append("")
lines.append("## $ Impact (modeled)")
lines.append(read_txt(impact_txt))
lines.append("")
lines.append("## Prioritization summary")
lines.append(read_txt(prio_txt))
lines.append("")
lines.append("## Recommended next moves")
lines.append("- Enforce SLAs & add ETA buffers in top late% states (target 3–5 pp reduction).")
lines.append("- Coach or re-route high-late sellers; institute probation for repeat offenders.")
lines.append("- Proactive delay comms + small credit to protect reviews on unavoidable delays.")
lines.append("- Weekly control-tower: late%, avg delay, review trend, repeat_90d; monthly ROI roll-up.")
with open(out_md, "w", encoding="utf-8") as f:
    f.write('\n'.join(lines))

print(f"Wrote insights -> {out_md}")
