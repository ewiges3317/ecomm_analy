import os
import shutil
import pandas as pd

BASE = r"data\processed\analysis"
DOCS = r"docs"
OUT_DIR = r"outputs\reports"
PACK_DIR = os.path.join(OUT_DIR, "exec_csv_pack")
os.makedirs(PACK_DIR, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

# Files we expect from earlier steps
wanted = [
    "kpi_late_by_state.csv",
    "kpi_review_by_delay_bucket.csv",
    "kpi_repeat_by_review_star.csv",
    "kpi_repeat_by_late.csv",
    "kpi_aov_by_late.csv",
    "impact_by_state.csv",
    "prioritize_states.csv",
    "prioritize_sellers.csv",
    "seller_by_state_matrix.csv",
    "journey_delivery_csat_repeat.csv",  # full joined data (big)
]

# Copy any that exist
copied = []
missing = []
for name in wanted:
    src = os.path.join(BASE, name) if name.endswith(".csv") else None
    if src and os.path.exists(src):
        dst = os.path.join(PACK_DIR, name)
        shutil.copy2(src, dst)
        copied.append(name)
    else:
        missing.append(name)

# Make top-10 samples for quick view
samples = []
for name in copied:
    try:
        df = pd.read_csv(os.path.join(PACK_DIR, name), low_memory=False)
        head = df.head(10)
        sample_path = os.path.join(PACK_DIR, name.replace(".csv","_TOP10.csv"))
        head.to_csv(sample_path, index=False)
        samples.append(os.path.basename(sample_path))
    except Exception:
        pass

# Write a README describing contents
readme_path = os.path.join(PACK_DIR, "README_EXEC_CSV_PACK.txt")
lines = []
lines.append("EXEC CSV PACK — Delivery → CSAT → Repeat")
lines.append("")
lines.append("Included files:")
for n in copied:
    lines.append(f"- {n}")
if samples:
    lines.append("")
    lines.append("Quick samples (first 10 rows):")
    for s in samples:
        lines.append(f"- {s}")
if missing:
    lines.append("")
    lines.append("Missing (not generated yet):")
    for m in missing:
        lines.append(f"- {m}")
lines.append("")
lines.append("Notes:")
lines.append("- Use *kpi_late_by_state.csv* to see late% and volume by state.")
lines.append("- *kpi_review_by_delay_bucket.csv* links delay to CSAT.")
lines.append("- *kpi_repeat_by_review_star.csv* shows retention gradient by review score.")
lines.append("- *kpi_repeat_by_late.csv* compares repeat rates on-time vs late.")
lines.append("- *impact_by_state.csv* and *prioritize_*.csv rank where to fix first by $ lift.")
lines.append("- *journey_delivery_csat_repeat.csv* is the joined table for deeper analysis.")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

# Zip the pack for easy sharing
zip_base = os.path.join(OUT_DIR, "exec_csv_pack")
shutil.make_archive(zip_base, "zip", PACK_DIR)

print("Pack created:")
print(" -", PACK_DIR)
print(" -", zip_base + ".zip")
print("README:", readme_path)
