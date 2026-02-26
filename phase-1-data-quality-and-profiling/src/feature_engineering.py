"""
Phase 1: Feature engineering.

Adds derived columns to the cleaned (processed) dataset: resolution_duration_hours,
sla_breach_flag, resolution_time_bucket, response_time_bucket, days_since_purchase,
description_word_count, subject_word_count, response_hour, response_day_of_week,
contains_urgent_language, contains_refund_language, is_pending_customer.
Input is the processed CSV (cleaning only); output is saved to data/featured/.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

import sys
_config_parent = Path(__file__).resolve().parent.parent
if str(_config_parent) not in sys.path:
    sys.path.insert(0, str(_config_parent))
from config import (
    sla_threshold_hours,
    response_time_bins,
    response_time_labels,
    FEATURED_DATA_PATH,
    ensure_output_dirs,
)


def _compute_resolution_duration_hours(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute resolution duration in hours: (resolution_time - first_response_time).
    """
    df = df.copy()
    start = df["first_response_time"]
    end = df["resolution_time"]
    delta = end - start
    df["resolution_duration_hours"] = delta.dt.total_seconds() / 3600.0
    return df


def _compute_first_response_duration_placeholder(df: pd.DataFrame) -> pd.DataFrame:
    """
    First response duration (hours) is not computable without ticket creation time.
    Column left as null for schema consistency.
    """
    df = df.copy()
    df["first_response_duration_hours"] = np.nan
    return df


def _apply_sla_breach_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag tickets that exceeded SLA based on priority and resolution duration.
    SLA thresholds (hours): Critical=4, High=8, Medium=24, Low=48.
    """
    df = df.copy()
    threshold = df["priority"].map(sla_threshold_hours)
    df["sla_breach_flag"] = (df["resolution_duration_hours"] > threshold).astype("Int64")
    df.loc[df["resolution_duration_hours"].isna(), "sla_breach_flag"] = np.nan
    df.loc[~df["priority"].isin(sla_threshold_hours.keys()), "sla_breach_flag"] = np.nan
    return df


def _bucket_resolution_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize resolution duration into bins: < 1h, 1-4h, 4-12h, 12-24h, 24+ h.
    """
    df = df.copy()
    df["resolution_time_bucket"] = pd.cut(
        df["resolution_duration_hours"],
        bins=response_time_bins,
        labels=response_time_labels,
        include_lowest=True,
    )
    return df


def _bucket_response_time(df: pd.DataFrame) -> pd.DataFrame:
    """
    First response duration not available; bucket left null for schema consistency.
    """
    df = df.copy()
    df["response_time_bucket"] = pd.NA
    return df


def _compute_days_since_purchase(df: pd.DataFrame) -> pd.DataFrame:
    """
    Days since purchase: (first_response_time - purchase_date).
    Null if purchase_date dropped for MVP or column missing.
    """
    df = df.copy()
    date_col = "purchase_date" if "purchase_date" in df.columns else "Date of Purchase"
    if date_col not in df.columns or "first_response_time" not in df.columns:
        df["days_since_purchase"] = np.nan
        return df
    delta = df["first_response_time"] - df[date_col]
    df["days_since_purchase"] = delta.dt.total_seconds() / (3600.0 * 24)
    return df


def _compute_word_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Extract word counts across description and subject fields."""
    df = df.copy()
    if "description" in df.columns:
        df["description_word_count"] = df["description"].fillna("").astype(str).str.split().str.len()
    if "subject" in df.columns:
        df["subject_word_count"] = df["subject"].fillna("").astype(str).str.split().str.len()
    return df


def _compute_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract hour and day of week of the first response."""
    df = df.copy()
    if "first_response_time" in df.columns:
        df["response_hour"] = df["first_response_time"].dt.hour
        df["response_day_of_week"] = df["first_response_time"].dt.day_name()
    return df


def _compute_keyword_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Flag tickets containing urgent or refund-related language."""
    df = df.copy()
    
    # Safely combine subject and description text
    desc = df["description"].fillna("").astype(str).str.lower() if "description" in df.columns else pd.Series(index=df.index, data="", dtype=str)
    subj = df["subject"].fillna("").astype(str).str.lower() if "subject" in df.columns else pd.Series(index=df.index, data="", dtype=str)
    text = desc + " " + subj
    
    urgent_keywords = ["urgent", "immediately", "emergency", "asap", "lawyer", "sue", "unacceptable"]
    refund_keywords = ["refund", "money back", "cancel", "return"]
    
    urgent_pattern = r"\b(?:" + "|".join(urgent_keywords) + r")\b"
    refund_pattern = r"\b(?:" + "|".join(refund_keywords) + r")\b"
    
    df["contains_urgent_language"] = text.str.contains(urgent_pattern, case=False, regex=True).fillna(False).astype(int)
    df["contains_refund_language"] = text.str.contains(refund_pattern, case=False, regex=True).fillna(False).astype(int)
    
    return df


def _compute_customer_delay_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Flag tickets that are currently pending customer response."""
    df = df.copy()
    if "status" in df.columns:
        df["is_pending_customer"] = (df["status"] == "Pending Customer Response").astype(int)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all feature-engineered columns to a cleaned (processed) DataFrame.

    Expects parsed datetime columns first_response_time, resolution_time (renamed in preprocessing);
    optional purchase_date for days_since_purchase (null if column dropped for MVP).
    Returns DataFrame with additional columns: resolution_duration_hours,
    first_response_duration_hours, sla_breach_flag, resolution_time_bucket,
    response_time_bucket, days_since_purchase, description_word_count,
    subject_word_count, response_hour, response_day_of_week,
    contains_urgent_language, contains_refund_language, is_pending_customer.
    """
    df = _compute_resolution_duration_hours(df)
    df = _compute_first_response_duration_placeholder(df)
    df = _apply_sla_breach_flag(df)
    df = _bucket_resolution_time(df)
    df = _bucket_response_time(df)
    df = _compute_days_since_purchase(df)
    df = _compute_word_counts(df)
    df = _compute_time_features(df)
    df = _compute_keyword_flags(df)
    df = _compute_customer_delay_flag(df)
    return df


def save_featured_data(df: pd.DataFrame, output_path: Optional[Path] = None) -> Path:
    """
    Write feature-engineered DataFrame to CSV in data/featured/.

    Uses FEATURED_DATA_PATH from config if output_path is None.
    """
    output_path = output_path or FEATURED_DATA_PATH
    ensure_output_dirs()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def run_feature_engineering(
    input_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Load processed CSV, add features, save to featured path. Returns featured DataFrame.

    If input_path is None, loads from config processed_data_path (caller must ensure
    processed file exists). If output_path is None, uses config FEATURED_DATA_PATH.
    """
    from config import processed_data_path

    path = input_path or processed_data_path
    if not Path(path).exists():
        raise FileNotFoundError(f"Processed data not found: {path}. Run cleaning first.")
    df = pd.read_csv(path)
    for col in ["first_response_time", "resolution_time", "purchase_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df = add_features(df)
    save_featured_data(df, output_path)
    return df
