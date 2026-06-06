"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BACKEND_SRC = ROOT / "app" / "backend" / "src"
MODELING_SRC = ROOT / "modeling" / "src"

# Must be set before backend modules import settings.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

sys.path.insert(0, str(BACKEND_SRC))
sys.path.insert(0, str(MODELING_SRC))


@pytest.fixture(scope="session")
def project_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def model_artifacts_available(project_root: Path) -> bool:
    models_dir = project_root / "modeling" / "models"
    return (
        (models_dir / "final_model.joblib").exists()
        and (models_dir / "preprocessor.joblib").exists()
    )


@pytest.fixture
def sample_predict_payload() -> dict:
    return {
        "gdp_per_capita": 3200.0,
        "gov_expenditure": 18.5,
        "debt_service_pct": 12.0,
        "external_debt_pct": 55.0,
        "gni_per_capita_growth": -2.1,
        "unemployment": 14.5,
        "fx_reserves_months": 2.1,
        "current_account_pct": -6.5,
        "trade_openness": 72.0,
        "inflation": 8.3,
        "fdi_inflows": 1.2,
        "region": "Middle East & North Africa",
        "income_group": "Lower middle income",
        "lending_type": "IBRD",
        "is_crisis_decade": "2010s",
    }
