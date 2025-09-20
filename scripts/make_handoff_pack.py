import os, shutil, glob

ROOT = r"."
DOCS = r"docs"
OUTP = r"outputs"
DASH = os.path.join(OUTP, "dashboards")
REPT = os.path.join(OUTP, "reports")

HANDOFF_DIR = os.path.join(REPT, "handoff_pack")
os.makedirs(HANDOFF_DIR, exist_ok=True)

# Always copy if present
files = [
    os.path.join(DOCS, "EXEC_1P_Delivery_CSAT_Repeat.md"),
    os.path.join(DOCS, "EXEC_Insights_Delivery_CSAT_Repeat.md"),
    os.path.join(DOCS, "impact_summary.txt"),
    os.path.join(DOCS, "prioritize_fixes_summary.txt"),
    os.path.join(DOCS, "EXEC_CHARTS_README.txt"),
    os.path.join(REPT, "exec_csv_pack.zip"),
    os.path.join(REPT, "Delivery_CSAT_Repeat_Executive.pptx"),
]

# Include the three PNG charts if present
files += sorted(glob.glob(os.path.join(DASH, "*.png")))

copied = []
for f in files:
    if os.path.exists(f):
        shutil.copy2(f, HANDOFF_DIR)
        copied.append(os.path.basename(f))

# Write a short README
readme = os.path.join(HANDOFF_DIR, "README_HANDOFF.txt")
with open(readme, "w", encoding="utf-8") as fh:
    fh.write("Delivery → CSAT → Repeat — Handoff Pack\n\n")
    fh.write("Included:\n")
    for n in copied:
        fh.write(f"- {n}\n")
    fh.write("\nHow to regenerate:\n")
    fh.write("1) Open CMD in project root\n")
    fh.write("2) Run: scripts\\run_all.bat\n")

# Zip it
zip_base = os.path.join(REPT, "handoff_pack")
shutil.make_archive(zip_base, "zip", HANDOFF_DIR)

print("Handoff pack created:")
print(" -", HANDOFF_DIR)
print(" -", zip_base + ".zip")
