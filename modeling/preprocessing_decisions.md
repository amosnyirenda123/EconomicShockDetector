# Preprocessing Decisions

This document records the Phase 2 preprocessing decisions for the Economic Shock Detector project. The goal is to keep the feature matrix usable for modeling while avoiding target leakage and inflated metrics.

## 1. Dropped Columns

The following columns are dropped entirely because their missingness rates are too high for reliable imputation:

- `domestic_credit_pct`: 86.75% missing.
- `govt_debt_pct_gdp`: 85.16% missing.

Keeping these variables would add noise and make the preprocessing pipeline less robust.

## 2. Row Drops

Rows with missing `gdp_per_capita` are dropped directly:

- Rows dropped: 82.
- Missing rate: 0.77%.

Because the missing rate is very small, dropping these rows is simpler and more reliable than imputing this variable before creating the log-transformed feature.

## 3. Leakage Decision

The following variables are dropped from the feature matrix:

- `gdp_growth`
- `gdp_growth_lag1`
- `gdp_growth_delta`

Reason: these variables were used directly to construct the target variable `gdp_shock`. Keeping them would allow the model to rediscover the labeling formula instead of learning genuine economic patterns.

Team decision: Option B, prioritizing intellectual honesty over artificially inflated performance.

Expected consequence: Phase 3 performance will likely be modest. After removing the target-defining variables, the remaining non-growth numeric indicators have correlations below 0.05 with `gdp_shock`; `gni_per_capita_growth` is the main remaining growth-related proxy and is not part of the exact target formula. This lower expected performance is deliberate and honest.

## 4. Missing Value Strategy

Missing numeric values are imputed using train-only median imputation grouped by `income_group`.

Applied to:

- `gov_expenditure`
- `debt_service_pct`
- `external_debt_pct`
- `gni_per_capita_growth`
- `unemployment`
- `fx_reserves_months`
- `current_account_pct`
- `trade_openness`
- `inflation`
- `fdi_inflows`

Justification: countries in the same income group tend to have more similar economic profiles, so an `income_group` median is more appropriate than a global median.

Leakage control: imputation statistics are fitted on the training set only. Validation and test sets are transformed using the medians learned from training data.

## 5. Outlier Strategy

Outliers are kept.

Known real extreme values:

- `current_account_pct`: approximately -148 to +312.
- `gdp_growth_delta`: approximately -126 to +137.

These values represent real economic events rather than data errors. The decision is to keep all outliers.

Consequence: numeric variables use `RobustScaler` instead of `StandardScaler`.

## 6. Scaler Choice

Use `RobustScaler` for all numeric variables.

Reason: `RobustScaler` is based on the median and interquartile range, making it resistant to extreme values. `StandardScaler` uses the mean and standard deviation, which would be distorted by the observed macroeconomic outliers.

## 7. Engineered Features

### `gdp_per_capita_log`

Formula:

```text
gdp_per_capita_log = np.log(gdp_per_capita)
```

Justification: `gdp_per_capita` spans approximately from $250 to $120,000 across countries. The log transform makes cross-country scale differences more economically proportional.

### `high_external_debt`

Formula:

```text
high_external_debt = 1 if external_debt_pct > 80 else 0
```

Justification: external debt above 80% of GNI is a standard economics threshold for debt vulnerability and crisis risk.

### Rejected Features

- `is_covid_year`: rejected because it would be approximately 97% zeros over a 60-year span and would mostly isolate one historical event.
- `inflation_shock`: rejected because inflation has near-zero correlation with `gdp_shock` in the EDA.

## 8. Encoding Decisions

- `region`: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` because it has 7 modalities and is purely nominal.
- `income_group`: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` because equal gaps between income levels are not guaranteed.
- `lending_type`: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` because it is nominal.
- `is_crisis_decade`: `OrdinalEncoder` because there is a clear temporal order: `1960s < 1970s < 1980s < 1990s < 2000s < 2010s < 2020s`.

## 9. Identifiers Excluded From Feature Matrix

The following identifiers are excluded from `X`:

- `country`
- `country_name`
- `year`

Reason: these are identifiers, not predictive features. Keeping them would encourage memorization or time/entity shortcuts rather than general economic learning.

## 10. Train / Validation / Test Split

Split proportions:

- Train: 70%.
- Validation: 15%.
- Test: 15%.

Split configuration:

- Stratified on `gdp_shock` to preserve the 8.3% minority class ratio.
- `random_state=42`.

Final saved dataset shapes, including the target column:

- `train.csv`: (7364, 30).
- `validation.csv`: (1578, 30).
- `test.csv`: (1579, 30).

Shock rates:

- Train: 8.28%.
- Validation: 8.24%.
- Test: 8.30%.

## 11. Imbalance Strategies Prepared for Phase 3

These strategies are documented for Phase 3 but are not implemented in Phase 2:

1. Baseline: no resampling, with `class_weight='balanced'` for models that support it.
2. Oversampling: `SMOTE` from `imbalanced-learn`.
3. Undersampling: `RandomUnderSampler` from `imbalanced-learn`.

Important: Phase 3 resampling workflows must use `imblearn.pipeline.Pipeline`, not `sklearn.pipeline.Pipeline`, so resampling is applied only during training and never to validation or test data.

## 12. Final Feature Matrix

The final transformed feature matrix has 29 features:

- 10 numeric features after train-only grouped median imputation and `RobustScaler`.
- 16 one-hot encoded categorical features.
- 1 ordinal encoded feature.
- 2 passthrough features.

The fitted preprocessing pipeline is serialized to:

```text
models/preprocessor.joblib
```
