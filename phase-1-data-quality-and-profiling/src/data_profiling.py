"""
Phase 1: Data profiling - structural audit and quality summary.

Produces a repeatable profile of the raw dataset (row/column counts, dtypes,
missing values, duplicate IDs, cardinality, numerical distributions) and
builds a data quality summary table for documentation.
"""

import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional

# -----------------------------------------------------------------------------
# Constants for profiling
# -----------------------------------------------------------------------------
CATEGORICAL_COLUMNS = [
    "Ticket Type",
    "Ticket Priority",
    "Ticket Channel",
    "Ticket Status",
    "Product Purchased",
]

NUMERICAL_DISTRIBUTION_COLUMNS = [
    "First Response Time",
    "Time to Resolution",
    "Customer Satisfaction Rating",
    "Customer Age",
]

TICKET_ID_COLUMN = "Ticket ID"


def load_raw_csv(file_path: Path) -> pd.DataFrame:
    """
    Load raw CSV with multiline-safe parsing.

    Ticket Description and other text fields may contain embedded newlines
    and quotes; the python engine handles these correctly.
    """
    return pd.read_csv(file_path, engine="python")


def profile_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Run full structural audit on the dataset.

    Returns a dictionary with:
      - row_count, column_count
      - dtypes (per column)
      - missing_counts, missing_pct (per column)
      - duplicate_ticket_ids: count and whether they look like re-opens vs true dupes
      - cardinality: unique value counts for categorical columns
      - numerical_distributions: describe() for selected numerical columns
    """
    profile = {}

    # Basic shape
    profile["row_count"] = len(df)
    profile["column_count"] = len(df.columns)
    profile["columns"] = list(df.columns)

    # Data types (as string for serialization)
    profile["dtypes"] = df.dtypes.astype(str).to_dict()

    # Missing values
    missing = df.isnull().sum()
    profile["missing_counts"] = missing.to_dict()
    profile["missing_pct"] = (missing / len(df) * 100).round(2).to_dict()

    # Duplicate Ticket IDs: count and sample for interpretation
    dup_ids = df[df.duplicated(subset=[TICKET_ID_COLUMN], keep=False)]
    profile["duplicate_ticket_id_count"] = dup_ids[TICKET_ID_COLUMN].nunique()
    profile["duplicate_ticket_id_rows"] = len(dup_ids)
    if profile["duplicate_ticket_id_rows"] > 0:
        sample = dup_ids.groupby(TICKET_ID_COLUMN).size()
        profile["duplicate_ticket_id_sample"] = sample.head(10).to_dict()

    # Cardinality of categorical fields
    profile["cardinality"] = {}
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            profile["cardinality"][col] = int(df[col].nunique())
            profile["cardinality_values_" + col] = df[col].dropna().unique().tolist()

    # Numerical distributions (only for columns that are numeric or parseable)
    profile["numerical_distributions"] = {}
    for col in NUMERICAL_DISTRIBUTION_COLUMNS:
        if col not in df.columns:
            continue
        ser = df[col]
        if pd.api.types.is_numeric_dtype(ser):
            profile["numerical_distributions"][col] = ser.describe().to_dict()
        else:
            profile["numerical_distributions"][col] = {"dtype": str(ser.dtype), "sample": ser.dropna().head(3).tolist()}

    return profile


def build_quality_summary(df: pd.DataFrame, profile: Dict[str, Any]) -> pd.DataFrame:
    """
    Build a data quality summary table: one row per column.

    Columns: column_name, completeness_pct, data_type, issues (brief text).
    """
    rows = []
    for col in df.columns:
        pct = 100 - profile["missing_pct"].get(col, 0)
        dtype = profile["dtypes"].get(col, "")
        issues = []

        if profile["missing_pct"].get(col, 0) > 0:
            issues.append(f"Missing {profile['missing_pct'][col]:.1f}%")
        if col in CATEGORICAL_COLUMNS and col in profile.get("cardinality", {}):
            card = profile["cardinality"][col]
            if card == 0:
                issues.append("All null")
            elif card == 1:
                issues.append("Single value")

        rows.append({
            "column_name": col,
            "completeness_pct": round(pct, 2),
            "data_type": str(dtype),
            "issues": "; ".join(issues) if issues else "None noted",
        })

    return pd.DataFrame(rows)
