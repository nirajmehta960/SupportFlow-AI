"""
Phase 1: Data Quality & Profiling - Pipeline runner.

Loads raw data, runs profiling, cleans and transforms, validates consistency,
saves processed output, and writes the data quality report and assumptions log.

Usage:
    python run_pipeline.py

Or from project root:
    python phase-1-data-quality-and-profiling/run_pipeline.py
"""

import sys
from pathlib import Path

# Ensure phase root is on path for config import
PHASE_ROOT = Path(__file__).resolve().parent
if str(PHASE_ROOT) not in sys.path:
    sys.path.insert(0, str(PHASE_ROOT))

from config import (
    RAW_DATA_PATH,
    processed_data_path,
    FEATURED_DATA_PATH,
    DATA_QUALITY_REPORT_PATH,
    ASSUMPTIONS_LOG_PATH,
    ensure_output_dirs,
)

from src.data_profiling import profile_data, build_quality_summary
from src.data_cleaning import (
    load_raw_data,
    clean_and_transform,
    save_processed_data,
    _validate_logical_consistency,
)
from src.feature_engineering import add_features, save_featured_data
from src.reporting import write_data_quality_report, write_assumptions_log


def main() -> None:
    # Create output directories
    ensure_output_dirs()

    # Load raw data
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw data not found: {RAW_DATA_PATH}")
    df_raw = load_raw_data(RAW_DATA_PATH)

    # 1.1 Initial data profiling
    profile = profile_data(df_raw)
    quality_summary_df = build_quality_summary(df_raw, profile)

    # 1.2 Data cleaning and transformation (drops bad data only: see data_cleaning._drop_bad_data)
    df_clean, clean_report = clean_and_transform(df_raw)
    df_clean, validation_report = _validate_logical_consistency(df_clean)
    validation_report["bad_data_drops"] = clean_report

    # Save processed (cleaned only) dataset
    saved_path = save_processed_data(df_clean)
    print(f"Processed data saved: {saved_path} ({len(df_clean)} rows)")

    # Feature engineering: add derived columns and save to data/featured/
    df_featured = add_features(df_clean)
    featured_path = save_featured_data(df_featured)
    print(f"Featured data saved: {featured_path} ({len(df_featured)} rows)")

    # 1.3 Data quality documentation
    write_data_quality_report(
        quality_summary_df,
        profile,
        validation_report,
        DATA_QUALITY_REPORT_PATH,
    )
    print(f"Data quality report written: {DATA_QUALITY_REPORT_PATH}")

    # CSAT missing stats and bad-data drop counts for assumptions log
    csat_missing = df_raw["Customer Satisfaction Rating"].isna().sum()
    csat_pct = (csat_missing / len(df_raw)) * 100
    write_assumptions_log(ASSUMPTIONS_LOG_PATH, int(csat_missing), csat_pct, clean_report)
    print(f"Assumptions log written: {ASSUMPTIONS_LOG_PATH}")

    print("Phase 1 pipeline complete.")


if __name__ == "__main__":
    main()
