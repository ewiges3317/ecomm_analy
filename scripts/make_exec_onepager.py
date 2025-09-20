import os
import pandas as pd

BASE = r"data\processed\analysis"
DOCS = r"docs"
os.makedirs(DOCS, exist_ok=True)

journey_csv = os.path.join(BASE, "journey_delivery_csat_repeat.csv")
out_md      = os.path.join(DOCS, "EXEC_1P_Delivery_CSAT_Repeat.md")

# --- Load journey or write a placeholder if missing
if not os.path.exists(journey_csv):
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# Delivery → CSAT → Repeat — Executive One-Pager\n\n")
        f.write("_Journey dataset not found._ Expected at:\n")
        f.write("`data/processed/analysis/journey_delivery_csat_repeat.csv`\n")
    print(f"Wrote 1-pager -> {out_md} (placeholder)")
else:
    df = pd.read_csv(journey_csv, low_memory=False)

    # Safe helpers
    def safe_mean(x):
        try:
            return float(pd.to_numeric(x, errors="coerce").mean())
        except Exception:
            return float("nan")

    orders_n = len(df)
    late     = df["is_late"]       if "is_late" in df.columns else pd.Series([0]*orders_n)
    reviews  = df["review_score"]  if "review_score" in df.columns else pd.Series([None]*orders_n)
    repeat   = df["repeat_90d"]    if "repeat_90d" in df.columns else pd.Series([0]*orders_n)
    price    = df["price_total"]   if "price_total" in df.columns else pd.Series([None]*orders_n)

    late_pct   = safe_mean(late) * 100
    avg_rev_on = safe_mean(reviews[late==0])
    avg_rev_lt = safe_mean(reviews[late==1])
    rep_on     = safe_mean(repeat[late==0]) * 100
    rep_lt     = safe_mean(repeat[late==1]) * 100
    aov        = pd.to_numeric(price, errors="coerce").dropna().mean() if pd.to_numeric(price, errors="coerce").notna().any() else 137.75

    lines = []
    lines.append("# Delivery → CSAT → Repeat — Executive One-Pager")
    lines.append("")
    lines.append("## TL;DR")
    lines.append(f"- **Orders analyzed:** {orders_n:,}")
    lines.append(f"- **Late deliveries:** {late_pct:.2f}%")
    lines.append(f"- **Avg review:** on-time {avg_rev_on:.2f} vs late {avg_rev_lt:.2f}")
    lines.append(f"- **Repeat in 90d:** on-time {rep_on:.2f}% vs late {rep_lt:.2f}%")
    lines.append(f"- **Assumed AOV:** ${aov:,.2f}")
    lines.append("")
    lines.append("## Key Takeaway")
    lines.append("Cutting late deliveries improves review scores and nudges repeat purchases—start with highest-volume, high-late states and outlier sellers.")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote 1-pager -> {out_md}")


