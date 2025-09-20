import os, pandas as pd
PROJECT_ROOT = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
src = os.path.join(PROJECT_ROOT, "data", "raw", "online_retail", "online_retail.xlsx")
dst = os.path.join(PROJECT_ROOT, "data", "raw", "online_retail", "online_retail.csv")
df = pd.read_excel(src)
df.to_csv(dst, index=False)
print("Wrote:", dst)
