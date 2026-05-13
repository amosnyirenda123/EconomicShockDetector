"""
Build Dataset — Person B
========================
Takes the raw CSV from data_collection.py and produces:
    - data/dataset.csv   (full clean labeled dataset)
    - data/sample.csv    (first 100 rows)

Cleaning steps applied:
    1. Drop rows where region is missing (World Bank aggregates, not real countries)
    2. Drop rows where gdp_growth is missing (cannot label without it)
    3. Drop rows where gdp_growth_lag1 is missing (cannot compute year-over-year drop)
    4. Apply target variable rule from cadrage section 4
    5. Verify all constraints before saving
"""

import pandas as pd
from pathlib import Path

# -----------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------
RAW_PATH     = Path(__file__).parent.parent / "data" / "economic_shock_dataset_raw.csv"
DATASET_PATH = Path(__file__).parent.parent / "data" / "dataset.csv"
SAMPLE_PATH  = Path(__file__).parent.parent / "data" / "sample.csv"

# -----------------------------------------------------------------------
# Load
# -----------------------------------------------------------------------
df = pd.read_csv(RAW_PATH)
print(f"Loaded raw dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

# -----------------------------------------------------------------------
# Step 1 — Drop aggregate/non-country rows (missing region = not a real country)
# -----------------------------------------------------------------------
before = len(df)
df = df.dropna(subset=["region"])
print(f"After dropping missing region:       {len(df):,} rows  (dropped {before - len(df):,})")

# -----------------------------------------------------------------------
# Step 2 — Drop rows where gdp_growth is missing (cannot apply target rule)
# -----------------------------------------------------------------------
before = len(df)
df = df.dropna(subset=["gdp_growth"])
print(f"After dropping missing gdp_growth:   {len(df):,} rows  (dropped {before - len(df):,})")

# -----------------------------------------------------------------------
# Step 3 — Drop rows where gdp_growth_lag1 is missing (first year per country)
# -----------------------------------------------------------------------
before = len(df)
df = df.dropna(subset=["gdp_growth_lag1"])
print(f"After dropping missing lag1:         {len(df):,} rows  (dropped {before - len(df):,})")

# -----------------------------------------------------------------------
# Step 4 — Apply target variable rule (cadrage section 4)
#
# economic_shock = 1 if ALL of:
#   - gdp_growth < 0          (economy actually contracted)
#   - gdp_growth_delta < -4   (dropped more than 4 percentage points vs prior year)
#   - gdp_growth_lag1 > 0     (prior year was positive — shock is sudden not ongoing)
# -----------------------------------------------------------------------
df["economic_shock"] = (
    (df["gdp_growth"]       <  0) &
    (df["gdp_growth_delta"] < -4) &
    (df["gdp_growth_lag1"]  >  0)
).astype(int)

# -----------------------------------------------------------------------
# Step 5 — Verify constraints
# -----------------------------------------------------------------------
print("\n--- Constraint Verification ---")

total_rows = len(df)
minority   = df["economic_shock"].sum()
minority_pct = minority / total_rows * 100

print(f"Total rows:         {total_rows:,}  (required: ≥ 10,000)")
print(f"Total columns:      {df.shape[1]}  (required: ≥ 8)")
print(f"Minority class:     {minority:,} rows = {minority_pct:.1f}%  (required: 5–25%)")
print(f"\nClass distribution:")
print(df["economic_shock"].value_counts())
print(df["economic_shock"].value_counts(normalize=True).round(3))

# Warn if constraints are not met
if total_rows < 10_000:
    print("\n⚠️  WARNING: fewer than 10,000 rows — go back and extend the year range")
if not (5 <= minority_pct <= 25):
    print(f"\n⚠️  WARNING: minority class is {minority_pct:.1f}% — adjust the threshold in the target rule")
else:
    print("\n✅ All constraints met")

# -----------------------------------------------------------------------
# Step 6 — Save
# -----------------------------------------------------------------------
df.to_csv(DATASET_PATH, index=False)
df.head(100).to_csv(SAMPLE_PATH, index=False)

print(f"\nSaved dataset.csv  → {DATASET_PATH}")
print(f"Saved sample.csv   → {SAMPLE_PATH}")
print(f"Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")