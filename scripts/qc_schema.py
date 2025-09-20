# -*- coding: utf-8 -*-
# QC + schema snapshot for raw datasets -> docs/schema_report.csv

import os, csv
import pandas as pd

PROJECT_ROOT = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW_DIRS = [
    os.path.join(PROJECT_ROOT, "data", "raw", "brazilian_ecommerce"),
    os.path.join(PROJECT_ROOT, "data", "raw", "online_retail"),
    os.path.join(PROJECT_ROOT, "data", "raw", "synthetic"),
]
DOCS = os.path.join(PROJECT_ROOT, "docs")
os.makedirs(DOCS, exist_ok=True)
out_csv = os.path.join(DOCS, "schema_report.csv")

rows = []
for d in RAW_DIRS:
    if not os.path.isdir(d):
        continue
    for root, _, files in os.walk(d):
        for fn in files:
            p = os.path.join(root, fn)
            lower = fn.lower()
            rec = {
                "relative_path": os.path.relpath(p, PROJECT_ROOT),
                "filename": fn,
                "rows": "",
                "n_cols": "",
                "columns": "",
                "dtypes": "",
                "notes": "",
            }
            try:
                if lower.endswith(".csv"):
                    df = pd.read_csv(p, nrows=250)   # sample only
                    rec["n_cols"] = len(df.columns)
                    rec["columns"] = "|".join(map(str, df.columns))
                    rec["dtypes"]  = "|".join([f"{c}:{str(t)}" for c,t in df.dtypes.items()])
                    # quick row count without loading whole file
                    with open(p, "rb") as f:
                        rec["rows"] = max(sum(1 for _ in f) - 1, 0)
                elif lower.endswith(".xlsx"):
                    xf = pd.ExcelFile(p)
                    first = xf.sheet_names[0]
                    df = xf.parse(first, nrows=250)
                    rec["n_cols"] = len(df.columns)
                    rec["columns"] = "|".join(map(str, df.columns))
                    rec["dtypes"]  = "|".join([f"{c}:{str(t)}" for c,t in df.dtypes.items()])
                    rec["rows"] = ""  # skip heavy count for xlsx
                else:
                    rec["notes"] = "skipped (not csv/xlsx)"
            except Exception as e:
                rec["notes"] = f"error: {e}"
            rows.append(rec)

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["relative_path","filename","rows","n_cols","columns","dtypes","notes"])
    w.writeheader()
    w.writerows(rows)

print("Wrote schema report ->", out_csv)
