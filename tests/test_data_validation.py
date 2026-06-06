"""Tests for data_validation helpers."""

import pandas as pd

from data_validation import (
    check_logical_inconsistencies,
    detect_outliers_iqr,
    detect_outliers_zscore,
    missing_value_summary,
)


def test_missing_value_summary():
    df = pd.DataFrame({"a": [1, None, 3], "b": [1, 2, 3]})
    report = missing_value_summary(df)
    assert report.loc[report["variable"] == "a", "missing_count"].iloc[0] == 1


def test_logical_inconsistency_negative_gdp():
    df = pd.DataFrame({"gdp_per_capita": [1000.0, -5.0, 2000.0]})
    issues = check_logical_inconsistencies(df)
    assert not issues.empty
    assert issues.iloc[0]["row_count"] == 1


def test_outlier_detection_iqr():
    df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 100]})
    report = detect_outliers_iqr(df, ["x"])
    assert report.iloc[0]["outlier_count"] >= 1


def test_outlier_detection_zscore():
    df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 100]})
    report = detect_outliers_zscore(df, ["x"])
    assert report.iloc[0]["outlier_count"] >= 1
