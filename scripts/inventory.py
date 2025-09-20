# -*- coding: utf-8 -*-
# inventories raw datasets -> docs/inventory.csv and docs/collection_log.txt
from pathlib import Path
import csv, hashlib
import pandas as pd

# Use repo-relative paths (portable across machines/OS)
from scripts._paths import ROOT, DATA_RAW, DOCS, RAW_BRAZIL, RAW_ONLINE_RETAIL, RAW_SYNTHETIC

RAW_DIRS = [RAW_BRAZIL, RAW_ONLINE_RETAIL, RAW_SYNTHETIC]

def md5(path: Path, block: int = 65536) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()

def csv_head_cols(path: Path, n: int = 50):
    try:
        df = pd.read_csv(path, nrows=n)
        return list(df.columns)
    except Exception:
        return []

def xlsx_cols_first_sheet(path: Path):
    try:
        xf = pd.ExcelFile(path)
        if xf.sheet_names:
            df = xf.parse(xf.sheet_names[0], nrows=5)
            return list(df.columns)
    except Exception:
        pass
    return []

def csv_fast_rowcount(path: Path):
    try:
        with path.open("rb") as f:
            return max(sum(1 for _ in f) - 1, 0)
    except Exception:
        return ""

def make_row(p: Path):
    rel = p.relative_to(ROOT).as_posix()
    size = p.stat().st_size
    hash_ = md5(p)
    rows = ""
    ncols = ""
    cols_preview = ""

    lower = p.suffix.lower()
    if lower == ".csv":
        cols = csv_head_cols(p)
        rows = csv_fast_rowcount(p)
        ncols = len(cols) if cols else ""
        cols_preview = ",".join(cols[:20]) if cols else ""
    elif lower == ".xlsx":
        cols = xlsx_cols_first_sheet(p)
        ncols = len(cols) if cols else ""
        cols_preview = ",".join(cols[:20]) if cols else ""

    return {
        "relative_path": rel,
        "filename": p.name,
        "size_bytes": size,
        "md5": hash_,
        "rows": rows,
        "n_cols": ncols,
        "columns_preview": cols_preview,
    }

# collect targets
targets = []
for d in RAW_DIRS:
    if d.is_dir():
        for p in d.rglob("*"):
            if p.is_file():
                targets.append(p)

# write inventory.csv
inv_csv = DOCS / "inventory.csv"
with inv_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(
        f,
        fieldnames=["relative_path", "filename", "size_bytes", "md5", "rows", "n_cols", "columns_preview"],
    )
    w.writeheader()
    for p in targets:
        w.writerow(make_row(p))

# write human-readable log
log_txt = DOCS / "collection_log.txt"
with log_txt.open("w", encoding="utf-8") as f:
    f.write("DATA COLLECTION INVENTORY\n")
    for p in targets:
        r = make_row(p)
        f.write(f"- {r['relative_path']} | size={r['size_bytes']} | rows={r['rows']} | cols={r['n_cols']}\n")

print("Wrote:", inv_csv)
print("Wrote:", log_txt)
