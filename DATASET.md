# Dataset documentation Economic Shock Detector

This document describes the analysis-ready dataset produced for the supervised learning project **Détection de chocs économiques soudains** (country × year). It aligns with the framing in `[cadrage.md](cadrage.md)` (source, target definition, features, and conformity checks).

---

## 1. Provenance and construction


| Stage                 | Artifact                                                           | Responsibility                                                   |
| --------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Collection            | Raw wide table from the World Bank (indicators + country metadata) | `src/data_collection.py` → `data/gdp_shock_dataset_raw.csv` |
| Processing & labeling | Cleaning, shock label, constraint checks, exports                  | `src/build-dataset.py` → `data/dataset.csv`, `data/sample.csv`   |


**API source:** [World Bank Indicators API](https://api.worldbank.org/v2/) — public, no authentication.  
**Helpdesk:** [World Bank Data Helpdesk](https://datahelpdesk.worldbank.org/knowledgebase/articles/889386).

The World Bank series codes used in collection are defined in `src/data_collection.py` (core indicators match `[cadrage.md](cadrage.md)` section9; additional series extend the panel for early-warning context).

---

## 2. Unit of observation

Each row is **one economy (country) in one calendar year**:

- **Grain:** country × year  
- **Not a row:** a quarter, a region aggregate, or a multi-year episode (aggregates with missing `region` are removed in the build step)

---

## 3. Coverage


| Dimension                      | Description                                                                                                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Time**                       | Default collection window in code: **1960–2022** (see `src/data_collection.py`). Actual min/max `year` in `dataset.csv` depend on availability after cleaning. |
| **Geography**                  | Countries and economies reported by the World Bank with valid metadata. Rows without `region` are dropped (non-country / aggregate series).                    |
| **Size (project requirement)** | **≥ 10,000 rows** after cleaning (`cadrage.md` section10). The exact count is printed when you run `src/build-dataset.py`.                                     |


---

## 4. Target variable: `gdp_shock`

**Type:** binary integer **0** or **1**.

**Labeling rule** (exact logic in `src/build-dataset.py`; definition from `[cadrage.md](cadrage.md)` section4):

`gdp_shock = 1` **only if all** of the following hold for that country-year:

1. **`gdp_growth` < 0** — annual real GDP growth is negative (contraction).
2. **`gdp_growth_delta` < −4** — growth fell by **more than 4 percentage points** versus the previous year.
3. **`gdp_growth_lag1` > 0** — the previous year’s growth was positive (the shock is **sudden**, not a continuation of an ongoing recession).

Otherwise **`gdp_shock = 0`**.

**Class balance (project requirement):** minority class (label **1**) should represent **between 5% and 25%** of rows (`cadrage.md` section10). The build script prints `value_counts` and `value_counts(normalize=True)` so you can verify this on the full `dataset.csv`.

---

## 5. Cleaning and row drops (`build-dataset.py`)

Rows are removed in this order:


| Step | Condition                    | Rationale                                                                                              |
| ---- | ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1    | `region` is missing          | Excludes World Bank aggregates that are not a single country.                                          |
| 2    | `gdp_growth` is missing      | Cannot apply the shock rule.                                                                           |
| 3    | `gdp_growth_lag1` is missing | Typically the **first year** per country in the panel; delta and sudden-shock logic need a prior year. |


Rows are **not** dropped solely because other indicators (e.g. unemployment) are missing; imputation or missing-value handling is deferred to modeling / Phase 2.

---

## 6. Column dictionary (`dataset.csv`)

Types below are logical types for modeling; CSV stores numbers and text as plain text.

### 6.1 Identifiers


| Column         | Type    | Description                             |
| -------------- | ------- | --------------------------------------- |
| `country`      | string  | ISO 3-letter economy code (World Bank). |
| `country_name` | string  | Human-readable economy name.            |
| `year`         | integer | Calendar year of observation.           |


### 6.2 Country metadata (World Bank classifications)


| Column         | Type   | Description                                               |
| -------------- | ------ | --------------------------------------------------------- |
| `region`       | string | World Bank geographical region.                           |
| `income_group` | string | Income group (e.g. Low income, High income).              |
| `lending_type` | string | Lending category (e.g. IDA, IBRD, Blend, Not classified). |


### 6.3 Core macro indicators (cadrage section9 and collection script)


| Column              | Type  | Typical unit | Notes                                                                  |
| ------------------- | ----- | ------------ | ---------------------------------------------------------------------- |
| `gdp_growth`        | float | % per year   | Annual % change of real GDP.                                           |
| `inflation`         | float | % per year   | Consumer price inflation.                                              |
| `unemployment`      | float | %            | Unemployment as % of labour force.                                     |
| `gdp_per_capita`    | float | constant USD | GDP per capita.                                                        |
| `external_debt_pct` | float | % of GNI     | External debt stock indicator (series mapped in `data_collection.py`). |
| `trade_openness`    | float | % of GDP     | Trade in goods and services relative to GDP.                           |
| `fdi_inflows`       | float | % of GDP     | Net FDI inflows relative to GDP.                                       |
| `gov_expenditure`   | float | % of GDP     | General government expense relative to GDP.                            |


### 6.4 Additional indicators (extended panel)


| Column                  | Type  | Typical unit | Description                         |
| ----------------------- | ----- | ------------ | ----------------------------------- |
| `current_account_pct`   | float | % of GDP     | Current account balance.            |
| `fx_reserves_months`    | float | months       | Foreign exchange reserves coverage. |
| `debt_service_pct`      | float | % of exports | Debt service on external debt.      |
| `govt_debt_pct_gdp`     | float | % of GDP     | Central government debt.            |
| `domestic_credit_pct`   | float | % of GDP     | Domestic credit to private sector.  |
| `gni_per_capita_growth` | float | % per year   | GNI per capita growth.              |


### 6.5 Engineered features


| Column             | Type   | Description                                                    |
| ------------------ | ------ | -------------------------------------------------------------- |
| `gdp_growth_lag1`  | float  | Previous year’s `gdp_growth` (same country).                   |
| `gdp_growth_delta` | float  | Change in GDP growth vs previous year (percentage **points**). |
| `is_crisis_decade` | string | Decade bucket (e.g. `1990s`, `2000s`) derived from `year`.     |


### 6.6 Target


| Column           | Type           | Description                          |
| ---------------- | -------------- | ------------------------------------ |
| `gdp_shock` | integer {0, 1} | **Supervised label** — see section4. |


---

## 7. Features vs target (for modeling)

For **supervised classification**, the **target** is `gdp_shock`.

**Identifiers** (usually excluded from feature matrix or used only for grouping): `country`, `country_name`, `year`.

**Candidate input features** include all remaining columns except `gdp_shock`. The project requires **at least 8** features after any feature selection (`cadrage.md` section10); this file provides **many** numeric and categorical columns so the team can choose a modeling subset while staying above the minimum.

---

## 8. Files and reproduction

From the project root (after dependencies are installed):

```bash
cd src
python data_collection.py
python build-dataset.py
```

Outputs:

- `data/gdp_shock_dataset_raw.csv` merged raw panel from the API.  
- `data/dataset.csv` cleaned, labeled dataset used for EDA and modeling.  
- `data/sample.csv` first 100 rows of `dataset.csv` for quick inspection.

---

## 9. Quality notes and limitations

- **Missing values:** After the GDP-based row drops, many indicators can still be missing for some country-years; treatment is a modeling choice.  
- **Revisions:** World Bank data can be revised over time; a rebuild can slightly change numbers.  
- **Definition of shock:** Labels depend **only** on the GDP growth rule in section4; other crises may not receive label **1**.  
- **Comparability:** Units follow World Bank metadata; cross-country comparison is standard for this source but still subject to measurement differences.

---

## 10. Discovery and verification

Exploratory analysis on the **full** `data/dataset.csv` should be recorded in `notebooks/01_discovery.ipynb` (e.g. `info`, `describe`, `head`, target `value_counts` and normalized counts, and a bar chart of class frequencies).

**Illustrative note:** `data/sample.csv` contains only the first **100** rows of `dataset.csv`. Any statistics computed on `sample.csv` alone are **not** representative of the full panel; always use `dataset.csv` for conformity checks and for reporting final class balance and row counts in coursework.