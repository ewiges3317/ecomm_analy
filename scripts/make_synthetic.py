# -*- coding: utf-8 -*-
# Generate synthetic marketing, customer_service, and marketing_spend CSVs

import os, random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

PROJECT_ROOT = r"C:\Users\jared\OneDrive\Documents\Ecom data\ecommerce_analytics_project"
RAW_BRAZIL = os.path.join(PROJECT_ROOT, "data", "raw", "brazilian_ecommerce")
RAW_SYNTH = os.path.join(PROJECT_ROOT, "data", "raw", "synthetic")
os.makedirs(RAW_SYNTH, exist_ok=True)

# Load customers from Olist
cust_csv = os.path.join(RAW_BRAZIL, "olist_customers_dataset.csv")
if not os.path.exists(cust_csv):
    raise FileNotFoundError(f"Missing {cust_csv} — extract Olist zip first.")

customers = pd.read_csv(cust_csv, usecols=["customer_id"])["customer_id"].dropna().astype(str).tolist()

# Reproducibility
random.seed(42)
np.random.seed(42)

channels = ["organic", "paid_search", "social", "email", "referral", "direct"]

# ------------------ 1) marketing_channels.csv ------------------
base_date = datetime(2016, 9, 4)
rows = []
for cid in customers:
    ch = random.choice(channels)
    acq_date = base_date + timedelta(days=random.randint(0, 800))
    acq_cost = float(np.random.gamma(2, 15)) if ch in {"paid_search", "social", "email"} else 0.0
    rows.append({
        "customer_id": cid,
        "acquisition_channel": ch,
        "acquisition_date": acq_date.strftime("%Y-%m-%d"),
        "acquisition_cost": round(acq_cost, 2),
        "campaign_id": f"CAMP_{random.randint(1000,9999)}",
        "utm_source": ch,
        "utm_medium": "cpc" if ch in {"paid_search", "social", "email"} else "organic",
    })
pd.DataFrame(rows).to_csv(os.path.join(RAW_SYNTH, "marketing_channels.csv"), index=False)

# ------------------ 2) customer_service.csv ------------------
svc_rows = []
issue_types = ["shipping", "product", "payment", "other"]
sample_ids = random.sample(customers, min(20000, len(customers)))
for cid in sample_ids:
    n = np.random.poisson(0.3)
    for _ in range(n):
        d0 = datetime(2016, 10, 1) + timedelta(days=random.randint(0, 730))
        hours = float(np.random.gamma(2, 24))
        svc_rows.append({
            "ticket_id": f"TICK_{random.randint(10000,99999)}",
            "customer_id": cid,
            "issue_date": d0.strftime("%Y-%m-%d"),
            "issue_type": random.choice(issue_types),
            "resolution_date": (d0 + timedelta(hours=hours)).strftime("%Y-%m-%d"),
            "satisfaction_score": int(np.random.choice([1,2,3,4,5], p=[0.05,0.10,0.15,0.40,0.30])),
            "resolution_time_hours": round(hours, 1),
        })
pd.DataFrame(svc_rows).to_csv(os.path.join(RAW_SYNTH, "customer_service.csv"), index=False)

# ------------------ 3) marketing_spend.csv ------------------
spend_rows = []
start = datetime(2016, 9, 1)
for m in range(25):
    cur = start + timedelta(days=30*m)
    month_year = cur.strftime("%Y-%m")
    for ch in channels:
        if ch in {"organic", "direct", "referral"}:
            spend = 0.0
            impressions = np.random.randint(50_000, 200_000)
            clicks = int(impressions * float(np.random.uniform(0.01, 0.03)))
        else:
            spend = float(np.random.gamma(5, 2000))
            impressions = int(spend * float(np.random.uniform(5, 15)))
            clicks = int(impressions * float(np.random.uniform(0.02, 0.08)))
        acquisitions = int(clicks * float(np.random.uniform(0.05, 0.15)))
        spend_rows.append({
            "month_year": month_year,
            "channel": ch,
            "spend_amount": round(spend, 2),
            "impressions": impressions,
            "clicks": clicks,
            "acquisitions": acquisitions,
        })
pd.DataFrame(spend_rows).to_csv(os.path.join(RAW_SYNTH, "marketing_spend.csv"), index=False)

print("✅ Wrote synthetic CSVs to:", RAW_SYNTH)
