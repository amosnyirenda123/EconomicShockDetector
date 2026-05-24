# Economic Shock Detector

Economic Shock Detector is a supervised machine learning project that predicts whether a country-year experienced a sudden economic shock. The dataset is built from the public World Bank Indicators API and models the target `gdp_shock` as a binary classification problem. Phase 2 is complete: EDA, leakage-safe preprocessing, train/validation/test splits, processed datasets, and the fitted preprocessing pipeline are ready for Phase 3 modeling.

## Project Structure

```text
EconomicShockDetector/
|-- .gitignore
|-- README.md
|-- cadrage.md
|-- DATASET.md
|-- preprocessing_decisions.md
|-- data/
|   |-- gdp_shock_dataset_raw.csv      # Raw merged World Bank panel
|   |-- dataset.csv                    # Cleaned labeled dataset
|   |-- sample.csv                     # First 100 rows of dataset.csv
|   `-- processed/
|       |-- train.csv                  # Preprocessed training set
|       |-- validation.csv             # Preprocessed validation set
|       `-- test.csv                   # Preprocessed test set
|-- models/
|   `-- preprocessor.joblib            # Fitted Phase 2 preprocessing pipeline
|-- notebooks/
|   |-- 01_discovery.ipynb             # Initial discovery notebook
|   |-- 02_eda.ipynb                   # Phase 2 exploratory analysis
|   `-- 03_preprocessing.ipynb         # Phase 2 preprocessing and exports
`-- src/
    |-- data_collection.py             # Fetches World Bank data
    |-- build-dataset.py               # Cleans data and builds labels
    |-- preprocessing.py               # Reusable preprocessing transformers
    `-- requirements.txt               # Project dependencies
```

## Phase Status

- Phase 1: COMPLETE
- Phase 2: COMPLETE
- Phase 3: IN PROGRESS
- Phase 4: NOT STARTED

## Reproduce Phase 2

Run these commands from the project root unless noted otherwise.

1. Collect raw World Bank data:

```bash
python src/data_collection.py
```

2. Build the cleaned labeled dataset:

```bash
python src/build-dataset.py
```

3. Run the EDA notebook:

```text
notebooks/02_eda.ipynb
```

4. Run the preprocessing notebook:

```text
notebooks/03_preprocessing.ipynb
```

## Dataset Summary

- Dataset before final preprocessing: 10,521 rows and 21 columns.
- Final transformed feature matrix: 29 features.
- Target: `gdp_shock`.
- Positive class rate: approximately 8.3%.
- Saved processed files:
  - `data/processed/train.csv`
  - `data/processed/validation.csv`
  - `data/processed/test.csv`

## Key Decisions

Full details are documented in `preprocessing_decisions.md`.

- Dropped `domestic_credit_pct` and `govt_debt_pct_gdp` due to more than 85% missing values.
- Dropped 82 rows with missing `gdp_per_capita`.
- Dropped `gdp_growth`, `gdp_growth_lag1`, and `gdp_growth_delta` to avoid target leakage.
- Excluded `country`, `country_name`, and `year` from the feature matrix as identifiers.
- Kept real macroeconomic outliers and used `RobustScaler`.
- Used train-only median imputation grouped by `income_group`.
- Encoded nominal categorical variables with one-hot encoding and `is_crisis_decade` with ordinal encoding.
- Prepared train/validation/test splits with stratification on `gdp_shock`.

## Phase 3 Handoff

Phase 3 should:

- Load `data/processed/train.csv`, `data/processed/validation.csv`, and `data/processed/test.csv`.
- Load `models/preprocessor.joblib` when raw-to-processed transformation needs to be reproduced.
- Train at least 4 models: Logistic Regression, Decision Tree, Random Forest, and XGBoost.
- Compare 3 imbalance strategies: baseline, SMOTE, and undersampling.
- Use Recall as the primary metric with target `Recall >= 0.80`.
- Track secondary metrics: `Precision >= 0.50`, `F1 >= 0.65`, and PR-AUC.
- Tune the best model with `GridSearchCV` or `RandomizedSearchCV`.
- Optimize the decision threshold using the asymmetric cost matrix from `cadrage.md`, where false negatives cost approximately 1000x more than false positives.
- Save the final model to `models/final_model.joblib`.
