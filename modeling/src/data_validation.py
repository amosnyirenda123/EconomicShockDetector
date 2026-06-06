"""Data quality checks: missing values, logical inconsistencies, and outliers."""

from __future__ import annotations

import numpy as np
import pandas as pd

# Columns that must not be negative (macroeconomic magnitudes).
NON_NEGATIVE_COLS = [
    "gdp_per_capita",
    "gov_expenditure",
    "debt_service_pct",
    "external_debt_pct",
    "fx_reserves_months",
    "trade_openness",
    "fdi_inflows",
]

# Percentage-like columns expected in [0, 100] when present.
PERCENT_RANGE_COLS = {
    "unemployment": (0.0, 100.0),
}


def missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing-rate table for every column."""
    rows = []
    for col in df.columns:
        missing = int(df[col].isna().sum())
        rows.append(
            {
                "variable": col,
                "missing_count": missing,
                "missing_pct": round(100 * missing / len(df), 4),
            }
        )
    return pd.DataFrame(rows).sort_values("missing_pct", ascending=False)


def check_logical_inconsistencies(df: pd.DataFrame) -> pd.DataFrame:
    """Detect impossible values and basic business-rule violations."""
    issues: list[dict] = []

    for col in NON_NEGATIVE_COLS:
        if col not in df.columns:
            continue
        mask = df[col].notna() & (df[col] < 0)
        if mask.any():
            issues.append(
                {
                    "check": f"negative_{col}",
                    "description": f"{col} must be >= 0",
                    "row_count": int(mask.sum()),
                    "action": "review_or_drop",
                }
            )

    for col, (lo, hi) in PERCENT_RANGE_COLS.items():
        if col not in df.columns:
            continue
        mask = df[col].notna() & ((df[col] < lo) | (df[col] > hi))
        if mask.any():
            issues.append(
                {
                    "check": f"range_{col}",
                    "description": f"{col} expected in [{lo}, {hi}]",
                    "row_count": int(mask.sum()),
                    "action": "review_or_clip",
                }
            )

    if "year" in df.columns:
        mask = df["year"].notna() & ((df["year"] < 1960) | (df["year"] > 2030))
        if mask.any():
            issues.append(
                {
                    "check": "year_range",
                    "description": "year outside plausible World Bank range [1960, 2030]",
                    "row_count": int(mask.sum()),
                    "action": "review_or_drop",
                }
            )

    if "gdp_per_capita" in df.columns:
        # Extreme but historically observed; flag only absurd values.
        mask = df["gdp_per_capita"].notna() & (df["gdp_per_capita"] > 250_000)
        if mask.any():
            issues.append(
                {
                    "check": "gdp_per_capita_extreme",
                    "description": "gdp_per_capita > 250k USD (likely data error)",
                    "row_count": int(mask.sum()),
                    "action": "review",
                }
            )

    return pd.DataFrame(issues)


def detect_outliers_iqr(
    df: pd.DataFrame,
    numeric_cols: list[str],
    factor: float = 1.5,
) -> pd.DataFrame:
    """Flag outliers using the Tukey IQR rule."""
    rows = []
    for col in numeric_cols:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        mask = df[col].notna() & ((df[col] < lower) | (df[col] > upper))
        rows.append(
            {
                "variable": col,
                "method": "IQR",
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4),
                "outlier_count": int(mask.sum()),
                "outlier_pct": round(100 * mask.sum() / len(df), 4),
            }
        )
    return pd.DataFrame(rows).sort_values("outlier_count", ascending=False)


def detect_outliers_zscore(
    df: pd.DataFrame,
    numeric_cols: list[str],
    threshold: float = 3.0,
) -> pd.DataFrame:
    """Flag outliers where |z| > threshold."""
    rows = []
    for col in numeric_cols:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if series.empty or series.std() == 0:
            continue
        z = (df[col] - series.mean()) / series.std()
        mask = df[col].notna() & (z.abs() > threshold)
        rows.append(
            {
                "variable": col,
                "method": "Z-score",
                "threshold": threshold,
                "outlier_count": int(mask.sum()),
                "outlier_pct": round(100 * mask.sum() / len(df), 4),
            }
        )
    return pd.DataFrame(rows).sort_values("outlier_count", ascending=False)


def outlier_decision_table(
    iqr_report: pd.DataFrame,
    keep_all: bool = True,
) -> pd.DataFrame:
    """Attach a keep/drop recommendation per variable."""
    if iqr_report.empty:
        return iqr_report
    result = iqr_report.copy()
    result["decision"] = "keep" if keep_all else "review"
    result["justification"] = (
        "Real macroeconomic extremes (crises, current-account swings); "
        "RobustScaler used instead of removal."
        if keep_all
        else "Manual review required."
    )
    return result
