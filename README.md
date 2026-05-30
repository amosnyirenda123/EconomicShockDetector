# Economic Shock Detector

> A supervised machine learning system that predicts whether a country-year experienced a sudden GDP economic shock, built on World Bank public indicators.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Screenshots

| Prediction Interface                                            | API Response                                                              |
| --------------------------------------------------------------- | ------------------------------------------------------------------------- |
| _[Screenshot: country selection and GDP shock prediction form]_ | _[Screenshot: JSON response with prediction, probability and confidence]_ |

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [With Docker (Recommended)](#with-docker-recommended)
  - [Without Docker](#without-docker)
- [API Documentation](#api-documentation)
- [Known Limitations](#known-limitations)
- [License](#license)

---

## Overview

The Economic Shock Detector models `gdp_shock` as a binary classification problem. Given a set of macroeconomic indicators for a country-year observation, the system predicts whether that country experienced a sudden economic shock and returns a probability score, a confidence label, and the decision threshold applied.

The full pipeline covers:

- **Data collection** — World Bank Indicators API
- **Preprocessing** — leakage-safe imputation, encoding, scaling, train/val/test splits
- **Modeling** — XGBoost with sampling strategies and threshold optimization
- **Serving** — FastAPI REST backend + Streamlit frontend, containerised with Docker

---

## Project Structure

```text
economic-shock-detector/
│
├── app/
│   ├── backend/                        # FastAPI backend service
│   │   ├── src/
│   │   │   ├── api/                    # Route definitions
│   │   │   ├── core/                   # Config and DB connection
│   │   │   ├── dependencies/           # FastAPI Depends factories
│   │   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── repository/             # Data access layer
│   │   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── scripts/                # init_db and utility scripts
│   │   │   ├── service/                # Business logic (ModelService, UserService)
│   │   │   └── main.py                 # FastAPI app entry point
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── .dockerignore
│   │
│   ├── frontend/                       # Streamlit frontend
│   │   ├── src/
│   │   │   ├── api/                    # HTTP client for backend
│   │   │   ├── components/             # Reusable UI components
│   │   │   ├── pages/                  # Multi-page app (home, predict, batch, developers)
│   │   │   ├── store/                  # Session state management
│   │   │   ├── app.py                  # Streamlit entry point
│   │   │   └── prediction_types.py     # Shared Pydantic types
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .dockerignore
│   │
│   └── docker-compose.yml
│
├── modeling/
│   ├── data/                           # Raw and processed datasets
│   ├── models/                         # Saved model and preprocessor artefacts
│   ├── notebooks/                      # EDA, preprocessing, modeling, evaluation
│   ├── src/                            # Reusable modeling helpers (GroupMedianImputer…)
│   └── preprocessing_decisions.md
│
├── scripts/                            # VM setup and maintenance scripts
│   ├── setup_vm.sh                     # Ubuntu 22.04
│   └── setup_vm.ps1                    # Windows Server / Windows 10-11
│
├── .gitignore
└── README.md
```

---

## Installation

### With Docker (Recommended)

**Prerequisites:** Docker Desktop (Windows/macOS) or Docker Engine + Compose (Linux).

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/economic-shock-detector.git
cd economic-shock-detector

# 2. Create your environment file
cp app/backend/.env.example app/backend/.env
# Edit .env with your DB password and model paths

# 3. Build and start all services
docker compose up --build -d

# 4. Initialise the database (first run only)
docker compose exec backend python scripts/init_db.py
```

| Service     | URL                         |
| ----------- | --------------------------- |
| Frontend    | http://localhost:8501       |
| Backend API | http://localhost:8000       |
| Swagger UI  | http://localhost:8000/docs  |
| ReDoc       | http://localhost:8000/redoc |

To stop: `docker compose down`

---

### Without Docker

#### Backend

```bash
cd app/backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your database URL and model paths

python src/scripts/init_db.py
uvicorn src.main:app --reload --port 8000
```

#### Frontend

```bash
cd app/frontend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
streamlit run src/app.py
```

#### VM Setup (fresh machine)

```powershell
# Windows — run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup_vm.ps1
```

```bash
# Ubuntu 22.04
chmod +x scripts/setup_vm.sh && ./scripts/setup_vm.sh
```

---

## API Documentation

Interactive documentation is auto-generated by FastAPI.

| Endpoint              | Method | Description                                   |
| --------------------- | ------ | --------------------------------------------- |
| `/`                   | GET    | API overview and documentation links          |
| `/health`             | GET    | Health check — confirms model is loaded       |
| `/model/info`         | GET    | Model type, threshold, training date, metrics |
| `/predict`            | POST   | Single prediction from JSON features          |
| `/predict/batch`      | POST   | Batch prediction from uploaded CSV file       |
| `/users/register`     | POST   | Register a new user                           |
| `/users/login`        | POST   | Login and retrieve user info                  |
| `/users/{id}/history` | GET    | Retrieve prediction history for a user        |

**Example — single prediction:**

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "gdp_per_capita": 3200.0,
    "unemployment": 14.5,
    "inflation": 8.3,
    "region": "Middle East & North Africa",
    "income_group": "Lower middle income",
    "lending_type": "IBRD",
    "is_crisis_decade": "2010s"
  }'
```

```json
{
  "prediction": "choc",
  "probability": 0.78,
  "threshold": 0.42,
  "confidence": "high"
}
```

---

## Known Limitations

| Limitation                  | Detail                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| **Data gaps**               | World Bank indicators have missing values for developing nations and earlier years          |
| **Temporal lag**            | Economic indicators are often revised months after initial publication                      |
| **Definition variability**  | The binary shock threshold is standardised and may not capture all country-specific nuances |
| **Geographic bias**         | Performance is stronger for OECD countries due to higher data quality and density           |
| **Unprecedented events**    | The model cannot predict shocks with no historical precedent (e.g. COVID-19)                |
| **Correlation ≠ causation** | The model identifies associated patterns, not causal relationships                          |
| **Retraining frequency**    | Quarterly retraining is recommended as new World Bank data is published                     |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

**Project status:** Phase 4 complete — modeling, API, frontend, and containerisation done.
