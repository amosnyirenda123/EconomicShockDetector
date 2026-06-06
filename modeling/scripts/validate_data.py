"""Run data-quality checks on dataset.csv (missing, inconsistencies, outliers)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_validation import (  # noqa: E402
    check_logical_inconsistencies,
    detect_outliers_iqr,
    detect_outliers_zscore,
    missing_value_summary,
    outlier_decision_table,
)


def main() -> None:
    data_path = ROOT / "data" / "dataset.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    print("=== Missing values ===")
    print(missing_value_summary(df).to_string(index=False))

    print("\n=== Logical inconsistencies ===")
    inconsistencies = check_logical_inconsistencies(df)
    if inconsistencies.empty:
        print("No inconsistencies detected.")
    else:
        print(inconsistencies.to_string(index=False))

    print("\n=== Outliers (IQR, factor=1.5) ===")
    iqr = detect_outliers_iqr(df, numeric_cols)
    print(outlier_decision_table(iqr).to_string(index=False))

    print("\n=== Outliers (Z-score, |z|>3) ===")
    zscore = detect_outliers_zscore(df, numeric_cols)
    print(zscore.to_string(index=False))


if __name__ == "__main__":
    main()
