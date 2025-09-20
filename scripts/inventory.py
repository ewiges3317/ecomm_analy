# -*- coding: utf-8 -*-
# inventories raw datasets -> docs/inventory.csv and docs/collection_log.txt

import os, csv, hashlib
import pandas as pd

PROJECT_ROOT = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW_DIRS = [
    os.path.join(PROJECT_ROOT, "data", "raw", "brazilian_ecommerce"),
    os.path.join(PROJECT_ROOT, "data", "raw", "online_retail"),
    os.path.join(PROJECT_ROOT, "data", "raw", "synthetic"),
]
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

def md5(path, block=65536):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()

def csv_head_cols(path, n=50):
    # try to read a small sample to get columns
    try:
        df = pd.read_csv(path, nrows=n)
        return list(df.columns)
    except Exception:
        return []

def xlsx_cols_first_sheet(path):
    try:
        xf = pd.ExcelFile(path)
        if xf.sheet_names:
            df = xf.parse(xf.sheet_names[0], nrows=5)
            return list(df.columns)
    except Exception:
        pass
    return []

def csv_fast_rowcount(path):
    # quick & cheap: line count minus header (won't load to RAM)
    try:
        with open(path, "rb") as f:
            return max(sum(1 for _ in f) - 1, 0)
    except Exception:
        return ""

def make_row(p):
    rel = os.path.relpath(p, PROJECT_ROOT)
    st = os.stat(p)
    size = st.st_size
    hash_ = md5(p)
    rows = ""
    ncols = ""
    cols_preview = ""

    lower = p.lower()
    if lower.endswith(".csv"):
        cols = csv_head_cols(p)
        rows = csv_fast_rowcount(p)
        ncols = len(cols) if cols else ""
        cols_preview = ",".join(cols[:20]) if cols else ""
    elif lower.endswith(".xlsx"):
        cols = xlsx_cols_first_sheet(p)
        ncols = len(cols) if cols else ""
        cols_preview = ",".join(cols[:20]) if cols else ""

    return {
        "relative_path": rel,
        "filename": os.path.basename(p),
        "size_bytes": size,
        "md5": hash_,
        "rows": rows,
        "n_cols": ncols,
        "columns_preview": cols_preview,
    }

# collect targets
targets = []
for d in RAW_DIRS:
    if os.path.isdir(d):
        for root, _, files in os.walk(d):
            for f in files:
                targets.append(os.path.join(root, f))

# write inventory.csv
inv_csv = os.path.join(DOCS_DIR, "inventory.csv")
with open(inv_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(
        f,
        fieldnames=["relative_path", "filename", "size_bytes", "md5", "rows", "n_cols", "columns_preview"],
    )
    w.writeheader()
    for p in targets:
        w.writerow(make_row(p))

# write human-readable log
log_txt = os.path.join(DOCS_DIR, "collection_log.txt")
with open(log_txt, "w", encoding="utf-8") as f:
    f.write("DATA COLLECTION INVENTORY\n")
    for p in targets:
        r = make_row(p)
        f.write(f"- {r['relative_path']} | size={r['size_bytes']} | rows={r['rows']} | cols={r['n_cols']}\n")

print("Wrote:", inv_csv)
print("Wrote:", log_txt)
