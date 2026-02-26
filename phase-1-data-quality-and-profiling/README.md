# Phase 1: Data Quality & Profiling

**Timeline:** Day 1–3  

**Objective:** Understand the shape, quality, and limitations of the dataset before any analysis begins.

**Relevant for:** Data Engineer, Data Analyst — establishing clean, documented, analysis-ready data.

## Overview

This phase ensures the Kaggle Customer Support Ticket Dataset is loaded, audited, cleaned, and transformed into an analysis-ready dataset. It also performs feature engineering (resolution duration, SLA breach flag, time buckets, days since purchase, text complexity, temporal features, and keyword flags) so the processed output is ready for Phase 2 analysis. All assumptions and cleaning decisions are documented for reproducibility.

## Key Activities

- **Initial data profiling** — Row/column counts, data types, missing values, duplicate Ticket IDs, cardinality of categorical fields, numerical distributions  
- **Data cleaning & transformation** — Standardize text, parse time fields, handle missing CSAT, validate logical consistency, create derived fields (SLA breach flag, response/resolution time buckets, days since purchase, text complexity, temporal features, and keyword flags)  
- **Data quality documentation** — Summary table per column, completeness, issues, and assumptions  

## Deliverables

| Deliverable | Description |
|-------------|-------------|
| Processed dataset | Cleaned-only CSV in `phase-1-data-quality-and-profiling/data/processed/` (e.g. `customer_support_tickets_processed.csv`) |
| Featured dataset | Cleaned + feature-engineered CSV in `phase-1-data-quality-and-profiling/data/featured/` (e.g. `tickets_featured.csv`) |
| Data quality report | Table and narrative in Jupyter Notebook; optional summary in `docs/data_quality_report.md` |

## Outputs Used Later

- **Featured CSV** (`data/featured/tickets_featured.csv`) is the input for **Phase 2: Support Operations Analysis** and **Phase 3: AI Solution Design** (includes derived columns: resolution_duration_hours, sla_breach_flag, time buckets, days_since_purchase, word counts, and language flags).  
- Data quality report and assumptions feed **Phase 4: Business Case & ROI** and **Phase 6: Deliverables & Presentation**.

## How to run

From the **project root** (SupportFlow AI):

```bash
# Ensure raw data is at phase-1-data-quality-and-profiling/data/raw/customer_support_tickets.csv
python phase-1-data-quality-and-profiling/run_pipeline.py
```

Outputs:

- `phase-1-data-quality-and-profiling/data/processed/customer_support_tickets_processed.csv` — cleaned dataset (preprocessing only)
- `phase-1-data-quality-and-profiling/data/featured/tickets_featured.csv` — cleaned + feature-engineered dataset for Phase 2 and Phase 3
- `docs/data_quality_report.md` — per-column summary and validation results
- `docs/assumptions_log.md` — SLA thresholds, CSAT handling, and other assumptions

Alternatively, run the Jupyter notebook `notebooks/01_data_profiling.ipynb` (same logic; interactive).

## See Also

- **IMPLEMENTATION_PLAN.md** — Step-by-step tasks for profiling, cleaning & transformation, and data quality documentation.
- **config.py** — Paths (raw, processed, featured) and SLA constants.
- **src/** — `data_profiling`, `data_cleaning`, `feature_engineering`, `reporting` modules.
