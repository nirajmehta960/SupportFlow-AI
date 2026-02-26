"""
Phase 1: Data Quality & Profiling - Configuration.

Centralizes paths and constants for reproducibility and environment-specific overrides.
SLA thresholds are based on industry benchmarks (see docs/assumptions_log.md).
"""

import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
# Phase root: directory containing this config (phase-1-data-quality-and-profiling)
PHASE_ROOT = Path(__file__).resolve().parent
# Project root: one level above phase root (SupportFlow AI)
PROJECT_ROOT = PHASE_ROOT.parent

# Raw input: Kaggle Customer Support Ticket Dataset
RAW_DATA_DIR = PHASE_ROOT / "data" / "raw"
RAW_DATA_FILE = "customer_support_tickets.csv"
RAW_DATA_PATH = RAW_DATA_DIR / RAW_DATA_FILE

# Processed output: cleaned dataset only (stored inside phase-1 only)
PROCESSED_DATA_DIR = PHASE_ROOT / "data" / "processed"
PROCESSED_DATA_FILE = "tickets_processed.csv"
processed_data_path = PROCESSED_DATA_DIR / PROCESSED_DATA_FILE

# Featured output: cleaned + feature-engineered dataset (stored inside phase-1 only)
FEATURED_DATA_DIR = PHASE_ROOT / "data" / "featured"
FEATURED_DATA_FILE = "tickets_featured.csv"
FEATURED_DATA_PATH = FEATURED_DATA_DIR / FEATURED_DATA_FILE

# Docs: data quality report and assumptions (project-level docs)
DOCS_DIR = PROJECT_ROOT / "docs"
DATA_QUALITY_REPORT_PATH = DOCS_DIR / "data_quality_report.md"
ASSUMPTIONS_LOG_PATH = DOCS_DIR / "assumptions_log.md"

# -----------------------------------------------------------------------------
# SLA thresholds (hours) - used for SLA breach flag
# Source: industry benchmarks; company-specific SLAs not present in dataset
# -----------------------------------------------------------------------------
sla_threshold_hours = {
    "Critical": 4,
    "High": 8,
    "Medium": 24,
    "Low": 48,
}

# -----------------------------------------------------------------------------
# Time buckets (hours) - for resolution time bucketing
# -----------------------------------------------------------------------------
response_time_bins = [0, 1, 4, 12, 24, float("inf")]
response_time_labels = ["< 1h", "1-4h", "4-12h", "12-24h", "24+ h"]

# -----------------------------------------------------------------------------
# Categorical columns to standardize (trim whitespace, normalize casing)
# -----------------------------------------------------------------------------
TEXT_STANDARDIZE_COLUMNS = [
    "Ticket Type",
    "Ticket Priority",
    "Ticket Channel",
    "Ticket Status",
]

# -----------------------------------------------------------------------------
# Columns to drop for MVP (preprocessing)
# Demographics and Date of Purchase not needed for ticket/operational analysis.
# -----------------------------------------------------------------------------
DROP_COLUMNS_MVP = [
    "Customer Name",
    "Customer Email",
    "Customer Age",
    "Customer Gender",
]

# -----------------------------------------------------------------------------
# Column renames (preprocessing) - original name -> snake_case
# Only columns present in df are renamed (dropped columns ignored).
# -----------------------------------------------------------------------------
RENAME_COLUMNS = {
    "Ticket ID": "ticket_id",
    "Ticket Type": "ticket_type",
    "Ticket Priority": "priority",
    "Ticket Channel": "channel",
    "Ticket Status": "status",
    "Ticket Subject": "subject",
    "Ticket Description": "description",
    "First Response Time": "first_response_time",
    "Time to Resolution": "resolution_time",
    "Customer Satisfaction Rating": "csat",
    "Resolution": "resolution_text",
    "Product Purchased": "product",
    "Date of Purchase": "purchase_date",
    "Customer Age": "customer_age",
    "Customer Gender": "customer_gender",
}

# -----------------------------------------------------------------------------
# Columns expected in raw data (for validation)
# -----------------------------------------------------------------------------
EXPECTED_COLUMNS = [
    "Ticket ID",
    "Customer Name",
    "Customer Email",
    "Customer Age",
    "Customer Gender",
    "Product Purchased",
    "Date of Purchase",
    "Ticket Type",
    "Ticket Subject",
    "Ticket Description",
    "Ticket Status",
    "Resolution",
    "Ticket Priority",
    "Ticket Channel",
    "First Response Time",
    "Time to Resolution",
    "Customer Satisfaction Rating",
]


def ensure_output_dirs():
    """Create output directories if they do not exist."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    FEATURED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


