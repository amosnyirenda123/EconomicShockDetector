"""Tests for ModelService prediction logic."""

import pytest

from schemas.schemas import PredictRequest
from service.model_service import ModelService, _add_engineered_features


def test_add_engineered_features():
    import pandas as pd

    df = pd.DataFrame({"gdp_per_capita": [1000.0], "external_debt_pct": [90.0]})
    out = _add_engineered_features(df)
    assert "gdp_per_capita_log" in out.columns
    assert out["high_external_debt"].iloc[0] == 1


def test_model_service_predict(project_root, sample_predict_payload, model_artifacts_available):
    if not model_artifacts_available:
        pytest.skip("final_model.joblib / preprocessor.joblib not found")

    import os

    models_dir = project_root / "modeling" / "models"
    os.environ["MODEL_PATH"] = str(models_dir / "final_model.joblib")
    os.environ["PREPROCESSOR_PATH"] = str(models_dir / "preprocessor.joblib")

    svc = ModelService()
    svc.load()
    assert svc._loaded

    request = PredictRequest(**sample_predict_payload)
    response = svc.predict(request)
    assert response.prediction in ("choc", "normal")
    assert 0.0 <= response.probability <= 1.0
