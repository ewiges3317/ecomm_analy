# scripts/_paths.py
from pathlib import Path

# Project root = parent of this file's folder (scripts/)
ROOT = Path(__file__).resolve().parents[1]

# Common dirs
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
SCRIPTS = ROOT / "scripts"

# Specific raw subdirs we use in this project
RAW_BRAZIL = DATA_RAW / "brazilian_ecommerce"
RAW_ONLINE_RETAIL = DATA_RAW / "online_retail"
RAW_SYNTHETIC = DATA_RAW / "synthetic"

# Ensure directories exist when scripts import this (safe no-ops if present)
for p in [DATA_PROCESSED, DOCS]:
    p.mkdir(parents=True, exist_ok=True)
