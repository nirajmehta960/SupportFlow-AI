"""
Phase 1: Data Quality & Profiling - Source package.

Exposes profiling, cleaning, and feature engineering for run_pipeline and notebooks.
"""

from .data_profiling import profile_data, build_quality_summary
from .data_cleaning import (
    load_raw_data,
    clean_and_transform,
    save_processed_data,
)
from .feature_engineering import add_features, save_featured_data, run_feature_engineering

__all__ = [
    "profile_data",
    "build_quality_summary",
    "load_raw_data",
    "clean_and_transform",
    "save_processed_data",
    "add_features",
    "save_featured_data",
    "run_feature_engineering",
]
