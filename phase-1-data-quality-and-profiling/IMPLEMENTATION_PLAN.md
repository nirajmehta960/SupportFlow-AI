# Phase 1: Data Quality & Profiling — Implementation Plan

**Days 1–3**

---

## 1.1 — Initial Data Profiling

- [ ] Load the dataset in Python (Pandas) and run a full structural audit.
- [ ] Document: total row count, column count, data types for each field.
- [ ] Check for missing values across every column — calculate missing percentage per field.
- [ ] Identify duplicate Ticket IDs (if any) and determine whether they represent true duplicates or re-opened tickets.
- [ ] Examine cardinality of categorical fields: unique values for **Ticket Type**, **Ticket Priority**, **Ticket Channel**, **Ticket Status**, **Product Purchased**.
- [ ] Profile numerical distributions: **First Response Time**, **Time to Resolution**, **Customer Satisfaction Rating**, **Customer Age**.

---

## 1.2 — Data Cleaning & Transformation

- [ ] **Standardize text fields:** Trim whitespace, normalize casing in Ticket Type, Priority, Channel, and Status.
- [ ] **Parse time fields:** Convert First Response Time and Time to Resolution into consistent numerical units (hours or minutes). Check whether they are stored as strings, timestamps, or numbers.
- [ ] **Handle missing Customer Satisfaction Ratings:** Document how many are missing; decide whether to exclude from CSAT analysis or impute (document decision).
- [ ] **Validate logical consistency:**
  - Does every "Closed" ticket have a Resolution value?
  - Do "Open" tickets have Time to Resolution = null (or equivalent)?
- [ ] **Create derived fields:**
  - **SLA Breach Flag:** Define SLA thresholds (e.g. Critical = 4h, High = 8h, Medium = 24h, Low = 48h). Flag tickets that exceeded their threshold based on Priority and Time to Resolution.
  - **Response/Resolution Time Buckets:** Categorize response and resolution times into bins (e.g. < 1h, 1–4h, etc.).
  - **Days Since Purchase:** If date fields are available, calculate the days since purchase.
  - **Text Complexity:** Calculate the word count for the subject and description to approximate ticket complexity.
  - **Temporal Features:** Extract the hour of day and day of week of the first response to analyze seasonality.
  - **Keyword Flags:** Create boolean flags for urgent language (e.g., "urgent", "lawyer") and refund language.
  - **Customer Delay Flag:** Flag if a ticket is currently waiting on the customer (Pending Customer Response).

---

## 1.3 — Data Quality Documentation

- [ ] Create a **data quality summary table**: each column, completeness, data type, and any issues found.
- [ ] Document all cleaning decisions and assumptions (e.g. "SLA thresholds were defined based on industry benchmarks since the dataset doesn't include company-specific SLAs").
- [ ] Ensure this is reflected in the Jupyter Notebook and, if desired, in `docs/data_quality_report.md` and `docs/assumptions_log.md`.

---

## Deliverables Checklist

- [ ] Clean, analysis-ready dataset saved as a processed CSV in `phase-1-data-quality-and-profiling/data/processed/`.
- [ ] Data quality report (table + narrative) in the notebook and/or `docs/`.
