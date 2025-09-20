# -*- coding: utf-8 -*-
# Reads docs/profile_core.csv -> prints issues worth eyeballing

import os, sys, math
import pandas as pd

PRJ = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
CSV = os.path.join(PRJ, "docs", "profile_core.csv")

df = pd.read_csv(CSV)

# Normalize types
df["null_pct"] = pd.to_numeric(df["null_pct"], errors="coerce").fillna(0.0)
df["unique_n"] = pd.to_numeric(df["unique_n"], errors="coerce")

print("\n=== HIGH-NULL COLUMNS (>=50%) ===")
hi = df[df["null_pct"] >= 50].sort_values(["file","null_pct"], ascending=[True,False])
if hi.empty:
    print("(none)")
else:
    for _,r in hi.iterrows():
        print(f"{r.file:32s} | {r.column:28s} | null%={r.null_pct:6.2f} | dtype={r.dtype}")

print("\n=== LIKELY DATE COLUMNS STILL STRINGS ===")
looks_date = df[
    (df["dtype"].str.contains("object")) &
    (df["column"].str.contains("date|timestamp|time", case=False, regex=True))
]
if looks_date.empty:
    print("(none)")
else:
    for _,r in looks_date.iterrows():
        print(f"{r.file:32s} | {r.column:35s} | dtype={r.dtype} | null%={r.null_pct:5.2f}")

print("\n=== SMALL-CARDINALITY CATEGORICALS (unique_n <= 30, not IDs) ===")
small = df[
    (df["unique_n"].notna()) &
    (df["unique_n"] <= 30) &
    (~df["column"].str.contains("id$", case=False)) &
    (~df["column"].str.contains("^id$", case=False))
].sort_values(["file","unique_n"])
if small.empty:
    print("(none)")
else:
    for _,r in small.iterrows():
        print(f"{r.file:32s} | {r.column:28s} | uniques={int(r.unique_n):4d} | null%={r.null_pct:5.2f}")

print("\n=== WIDE-NUMERIC COLUMNS (float/int) — potential outlier checks ===")
num = df[df["dtype"].str.contains("int|float")]
for f in num["file"].unique():
    cols = num[num["file"]==f]["column"].tolist()
    print(f"{f}: {', '.join(cols)}")
