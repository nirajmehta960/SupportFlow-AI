"""
Phase 1: Data cleaning and transformation (preprocessing only).

Standardize text, parse timestamps, then drop only bad data (invalid rows).
Valid behavior: Open/In Progress/Pending may have null Resolution Time and
maybe null First Response Time; Closed must have both timestamps. Bad data:
Closed with null timestamps, Time to Resolution < First Response Time,
negative time, CSAT present when ticket not Closed. Feature engineering is
in feature_engineering.py; output is saved to data/featured/.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

import sys
_config_parent = Path(__file__).resolve().parent.parent
if str(_config_parent) not in sys.path:
    sys.path.insert(0, str(_config_parent))
from config import (
    TEXT_STANDARDIZE_COLUMNS,
    DROP_COLUMNS_MVP,
    RENAME_COLUMNS,
    ensure_output_dirs,
    processed_data_path,
)
from .data_profiling import load_raw_csv


def load_raw_data(raw_path: Path) -> pd.DataFrame:
    """
    Load raw customer support tickets CSV.

    Uses python engine to handle multiline text in Ticket Description and
    other free-text fields.
    """
    return load_raw_csv(raw_path)


def _drop_columns_mvp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns not needed for MVP: demographics and Date of Purchase.

    Keeps focus on ticket-level and operational analysis (type, priority,
    channel, timestamps, CSAT). Demographics add no value for current
    bottlenecks/ROI; Date of Purchase is not used in MVP metrics.
    """
    df = df.copy()
    to_drop = [c for c in DROP_COLUMNS_MVP if c in df.columns]
    df = df.drop(columns=to_drop)
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns to snake_case for downstream use.
    Only renames columns that exist (dropped columns are skipped).
    """
    df = df.copy()
    mapping = {k: v for k, v in RENAME_COLUMNS.items() if k in df.columns}
    df = df.rename(columns=mapping)
    return df


def _standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trim whitespace and normalize to title case for categorical text columns.
    Reduces duplicate categories due to casing or spacing (e.g. '  Critical  ' -> 'Critical').
    """
    df = df.copy()
    for col in TEXT_STANDARDIZE_COLUMNS:
        if col not in df.columns:
            continue
        # Strip and title-case; leave nulls as null
        # Only standardize non-null values to avoid converting NaN to string "Nan"
        mask = df[col].notna()
        df.loc[mask, col] = df.loc[mask, col].astype(str).str.strip().str.title()
    return df


def _parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse First Response Time and Time to Resolution as datetimes.

    Converts to datetime64[ns]. Invalid or missing values become NaT.
    """
    df = df.copy()
    for col in ["First Response Time", "Time to Resolution"]:
        if col not in df.columns:
            continue
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _parse_date_of_purchase(df: pd.DataFrame) -> pd.DataFrame:
    """Parse Date of Purchase for ticket age (no-op if column dropped for MVP)."""
    df = df.copy()
    if "Date of Purchase" not in df.columns:
        return df
    df["Date of Purchase"] = pd.to_datetime(df["Date of Purchase"], errors="coerce")
    return df


def _normalize_status(s: pd.Series) -> pd.Series:
    """Normalize Ticket Status for comparison (strip, title case; NaN stays NaN)."""
    out = s.astype(object).fillna("").astype(str).str.strip().str.title()
    return out.replace("", np.nan)


def _drop_bad_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Drop rows that violate business rules (bad data only).

    Valid behavior (kept): Open (First Response maybe null, Resolution null);
    In Progress / Pending Customer Response (First Response exists, Resolution null);
    Closed (both exist). Bad data dropped:
    1. Closed but First Response Time or Time to Resolution is null.
    2. Both timestamps exist but Time to Resolution < First Response Time (negative duration).
    3. Customer Satisfaction Rating exists but ticket is not Closed.

    Returns (filtered df, report dict with drop counts per reason).
    """
    report = {
        "rows_dropped_closed_missing_timestamps": 0,
        "rows_dropped_negative_or_invalid_time": 0,
        "rows_dropped_csat_not_closed": 0,
    }
    n_before = len(df)
    status = _normalize_status(df["Ticket Status"])

    # 1. Closed ticket with null First Response Time or null Time to Resolution
    closed = status == "Closed"
    missing_first = df["First Response Time"].isna()
    missing_resolution = df["Time to Resolution"].isna()
    bad_closed = closed & (missing_first | missing_resolution)
    df = df.loc[~bad_closed].copy()
    report["rows_dropped_closed_missing_timestamps"] = int(bad_closed.sum())

    # 2. Both timestamps exist but Time to Resolution < First Response Time (invalid/negative)
    both = df["First Response Time"].notna() & df["Time to Resolution"].notna()
    invalid_order = both & (df["Time to Resolution"] < df["First Response Time"])
    df = df.loc[~invalid_order].copy()
    report["rows_dropped_negative_or_invalid_time"] = int(invalid_order.sum())

    # 3. CSAT exists but ticket is not Closed (CSAT should only exist when Closed)
    csat_exists = df["Customer Satisfaction Rating"].notna()
    not_closed = status != "Closed"
    bad_csat = csat_exists & not_closed
    df = df.loc[~bad_csat].copy()
    report["rows_dropped_csat_not_closed"] = int(bad_csat.sum())

    report["rows_dropped_total"] = n_before - len(df)
    return df, report


def _validate_logical_consistency(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Check logical consistency: Closed tickets have resolution_text; Open have null resolution_time.

    Expects df with renamed columns (status, resolution_text, resolution_time).
    Returns (df unchanged, validation_report dict with counts and any issues).
    """
    report = {}

    closed = df["status"].str.strip().str.title() == "Closed"
    open_status = df["status"].str.strip().str.title() == "Open"
    other_status = ~closed & ~open_status

    # Closed should have resolution_text
    closed_with_resolution = closed & df["resolution_text"].notna()
    closed_without_resolution = closed & df["resolution_text"].isna()
    report["closed_total"] = int(closed.sum())
    report["closed_missing_resolution"] = int(closed_without_resolution.sum())

    # Open should have null resolution_time (or we just document)
    open_with_resolution_time = open_status & df["resolution_time"].notna()
    report["open_total"] = int(open_status.sum())
    report["open_with_resolution_time"] = int(open_with_resolution_time.sum())

    report["validation_passed"] = (
        report["closed_missing_resolution"] == 0
        and report["open_with_resolution_time"] == 0
    )
    return df, report


def clean_and_transform(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Preprocessing only: drop MVP-unneeded columns, standardize text, parse
    datetimes, drop bad data. Valid rows kept; no feature engineering (see
    feature_engineering.py).

    Returns (cleaned DataFrame, report dict with rows_dropped_* counts).
    """
    df = _drop_columns_mvp(df)
    df = _standardize_text(df)
    df = _parse_datetime_columns(df)
    df = _parse_date_of_purchase(df)
    df, report = _drop_bad_data(df)
    df = _rename_columns(df)
    
    # Run logical consistency check after columns are renamed.
    df, val_report = _validate_logical_consistency(df)
    report.update(val_report)
    
    return df, report


def save_processed_data(df: pd.DataFrame, output_path: Optional[Path] = None) -> Path:
    """
    Write processed DataFrame to CSV for downstream phases.

    Ensures output directory exists. Uses default processed_data_path if output_path is None.
    """
    output_path = output_path or processed_data_path
    ensure_output_dirs()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path
