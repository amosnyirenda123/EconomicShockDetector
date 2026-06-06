# Economic Shock Detector — Modeling

Supervised ML project: predict `gdp_shock` (binary) from World Bank macroeconomic indicators.

## Phase status

| Phase | Status |
|-------|--------|
| Phase 1 — Cadrage & collecte | Complete (`cadrage.md`, `01_discovery.ipynb`) |
| Phase 2 — EDA & preprocessing | Complete (`02_eda.ipynb`, `03_preprocessing.ipynb`) |
| Phase 3 — Modélisation | Complete (`04`–`06` notebooks, `final_model.joblib`) |
| Phase 4 — Déploiement | Complete (`app/` FastAPI + Streamlit + Docker) |

## Key artefacts

| File | Description |
|------|-------------|
| `data/processed/train.csv` | Stratified train set (70 %) |
| `data/processed/validation.csv` | Validation set (15 %) |
| `data/processed/test.csv` | Test set (15 %) |
| `models/preprocessor.joblib` | Fitted sklearn preprocessing pipeline |
| `models/final_model.joblib` | Tuned XGBoost + optimal threshold metadata |
| `preprocessing_decisions.md` | All Phase 2 decisions per variable |

## Run data validation

```bash
python modeling/scripts/validate_data.py
```

## Re-run notebooks (optional)

Execute in order from `modeling/notebooks/`:

1. `02_eda.ipynb`
2. `03_preprocessing.ipynb` — exports processed CSVs and `preprocessor.joblib`
3. `04_modeling.ipynb` — 12 configurations (4 models × 3 sampling strategies)
4. `05_tuning.ipynb` — RandomizedSearchCV on best combo
5. `06_evaluation.ipynb` — test evaluation, threshold optimization, `final_model.joblib`

## Tests

From repository root:

```bash
pytest tests/test_data_validation.py -v
pytest tests/ -v   # full suite (needs model artefacts for API tests)
```

See root [README.md](../README.md#testing) for API, Docker, and UI testing.
