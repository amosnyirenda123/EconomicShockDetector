## Project Structure

```
EconomicShockDetector/
│
├── src/
│   ├── data_collection.py      ← fetches raw data from World Bank API
│   ├── build-dataset.py          ← cleans data and creates the final dataset
│   └── requirements.txt        ← dependencies of the project
│
├── data/
│   ├── gdp_shock_dataset_raw.csv         ← raw output from data_collection.py
│   ├── dataset.csv                      ← final clean labeled dataset
│   └── sample.csv                       ← first 100 rows for quick review
│
├── notebooks/
│   └── 01_discovery.ipynb        ← EDA on dataset.csv (Person C)
│
├── DATASET.md                    ← dataset documentation (Person C)
├── cadrage.md                    ← project framing (business objectives, metrics)
└── README.md
```

---

## How to Run

### Step 1 — Install dependencies
```bash
pip install -r src/requirements.txt
```
(From the **project root**. If your shell is already inside `src/`, use `pip install -r requirements.txt` instead.)

### Step 2 — Collect raw data from the World Bank API
```bash
cd src
python data_collection.py
```
This makes ~14 API calls to the World Bank.  
It takes about 5 to 15 minutes depending on your connection.  
Output: `data/gdp_shock_dataset_raw.csv`

### Step 3 — Build the final clean dataset
```bash
python build-dataset.py
```
This cleans the raw data, applies the shock labeling rule, and saves the final files.  
Output: `data/dataset.csv` and `data/sample.csv`

---

## The Data

### Where it comes from
World Bank Indicators API — `https://api.worldbank.org/v2/`  
No API key needed. Completely free and public.  
Data covers **~200 countries** from **1960 to 2022**.

### What each row looks like
One row = one country in one year.

| Column | Type | Description |
|---|---|---|
| `country` | text | ISO 3-letter country code (e.g. MAR, USA) |
| `country_name` | text | Full country name (e.g. Morocco, United States) |
| `year` | number | Year of observation |
| `gdp_growth` | number | Annual GDP growth % |
| `inflation` | number | Consumer price inflation % |
| `unemployment` | number | Unemployment % of labour force |
| `gdp_per_capita` | number | GDP per capita in constant USD |
| `external_debt_pct` | number | External debt as % of GNI |
| `trade_openness` | number | Trade as % of GDP |
| `fdi_inflows` | number | Foreign direct investment as % of GDP |
| `gov_expenditure` | number | Government expenditure as % of GDP |
| `current_account_pct` | number | Current account balance as % of GDP |
| `fx_reserves_months` | number | Foreign exchange reserves in months of imports |
| `debt_service_pct` | number | Debt service as % of exports |
| `govt_debt_pct_gdp` | number | Government debt as % of GDP |
| `domestic_credit_pct` | number | Domestic credit as % of GDP |
| `gni_per_capita_growth` | number | GNI per capita growth % |
| `region` | category | World region (e.g. Sub-Saharan Africa) |
| `income_group` | category | World Bank income classification |
| `lending_type` | category | World Bank lending classification |
| `is_crisis_decade` | category | Decade bucket (1980s, 1990s, 2000s...) |
| `gdp_growth_lag1` | number | GDP growth of the previous year |
| `gdp_growth_delta` | number | Change in GDP growth vs previous year (in percentage points) |
| `gdp_shock` | **0 or 1** | **Target variable — what we are predicting** |

---

## Cleaning Decisions

During `build-dataset.py` we drop rows in this order and for these reasons:

| What we drop | Why |
|---|---|
| Rows where `region` is missing | These are World Bank aggregate entries (e.g. "Arab World"), not real countries |
| Rows where `gdp_growth` is missing | Cannot apply the shock rule without GDP data |
| Rows where `gdp_growth_lag1` is missing | Cannot compute the year-over-year drop without the previous year's value — typically the first year of each country in the dataset |

We do **not** drop rows just because other indicators (inflation, unemployment, etc.) are missing. Those will be handled during preprocessing in Phase 2.

