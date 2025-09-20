\# Delivery → CSAT → Repeat (E-commerce Analytics)



A fast, stakeholder-ready analysis showing how delivery timeliness impacts customer satisfaction (CSAT) and 90-day repeat purchases. Built from the Olist Brazilian e-commerce dataset with reproducible scripts and executive-facing outputs.



\## 60-Second Summary

\- Orders analyzed: \*\*99,441\*\*

\- Late deliveries: \*\*6.57%\*\*

\- Avg review: \*\*on-time 4.21\*\* vs \*\*late 2.27\*\*

\- 90-day repeat rate: \*\*on-time 2.36%\*\* vs \*\*late 2.04%\*\*

\- Assumed AOV: \*\*$137.75\*\*

\- Takeaway: reducing late deliveries improves CSAT and nudges repeat behavior upward.



\## Where to Start (for reviewers)

1\. Read the 1-page brief: `docs/EXEC\_1P\_Delivery\_CSAT\_Repeat.md`

2\. Skim the insights: `docs/EXEC\_Insights\_Delivery\_CSAT\_Repeat.md`

3\. See the visuals (PNG): `outputs/dashboards/`

4\. Open the CSV “exec pack”: `outputs/reports/exec\_csv\_pack/`  

&nbsp;  (includes KPIs, state/seller prioritization, and the joined journey table)



\## Repo Map (high-level)

\- `docs/` – executive summaries and reproducibility notes  

\- `scripts/` – data build \& checks (`build\_journey.py`, `check\_joins.py`, etc.)  

\- `data/processed/analysis/` – ready-to-use analysis CSVs (joined journey + KPI cuts)  

\- `outputs/dashboards/` – charts used in the brief  

\- `outputs/reports/` – handoff packs (CSV pack + PPTX)



\## Reproducibility (current status)

\- Processed analysis CSVs are included so reviewers can verify results immediately.

\- Raw Olist data is \*\*not\*\* committed (size/licensing). Scripts expect local paths.

\- A dedicated `requirements.txt` and a simple `run\_all.bat` will be added next.



\## How It Works (nutshell)

\- Build journey: `scripts/build\_journey.py` joins orders, items, reviews, customers, and sellers, computes delivery delay, CSAT, and 90-day repeat flags.

\- Validate joins: `scripts/check\_joins.py` runs key sanity checks and join quality.

\- KPIs and “where to fix first” are derived from `data/processed/analysis/\*`.



\## What’s Next (roadmap)

\- Add `requirements.txt` (pandas, numpy, matplotlib, python-pptx, optional pyarrow)

\- Add `scripts/run\_all.bat` for one-click rebuild on Windows CMD

\- Add data path instructions / small synthetic sample for demo runs

\- Add lightweight unit checks (row counts, null rates) to CI



---



\*Contact \& Portfolio: add your links here.\*



