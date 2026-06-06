"""FastAPI integration tests for prediction endpoints."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from dependencies.dependencies import get_model_repository
from main import app


@pytest.fixture
def client():
    app.dependency_overrides[get_model_repository] = lambda: MagicMock()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "docs_url" in response.json()


def test_health(client, model_artifacts_available):
    response = client.get("/health")
    if model_artifacts_available:
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    else:
        assert response.status_code == 503


def test_predict(client, sample_predict_payload, model_artifacts_available):
    if not model_artifacts_available:
        pytest.skip("Model artefacts not found")

    response = client.post("/predict", json=sample_predict_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in ("choc", "normal")
    assert "probability" in body
    assert "threshold" in body
    assert body["confidence"] in ("high", "medium", "low")


def test_predict_invalid_payload(client, model_artifacts_available):
    if not model_artifacts_available:
        pytest.skip("Model artefacts not found")

    bad = {"gdp_per_capita": -100}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422
