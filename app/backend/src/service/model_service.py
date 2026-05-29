import io
import json
import logging
from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
import pandas as pd

from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from core.config import settings
from schemas.schemas import PredictRequest, PredictResponse

logger = logging.getLogger(__name__)


def _confidence_label(prob: float, threshold: float) -> str:
    distance = abs(prob - threshold)
    if distance >= 0.25:
        return "high"
    if distance >= 0.10:
        return "medium"
    return "low"


class ModelService:
    """Loaded ONCE at application startup. Repository is injected per-request."""

    def __init__(self):
        self.repository = None  # injected by dependency factory
        self._payload: dict = {}
        self._loaded = False

    

    def load(self):
        """Call once at startup (lifespan)."""
        model_path = Path(settings.model_path)
        if not model_path.exists():
            logger.warning(f"Model file not found at {model_path}. Health will report degraded.")
            return
        try:
            self._payload = joblib.load(model_path)
            self._loaded = True
            logger.info(f"Model loaded from {model_path}")
        except Exception as exc:
            logger.error(f"Failed to load model: {exc}")

    @property
    def pipeline(self):
        return self._payload.get("pipeline")

    @property
    def threshold(self) -> float:
        return float(self._payload.get("optimal_threshold", 0.5))

    @property
    def feature_names(self) -> list[str]:
        return self._payload.get("feature_names", [])

    

    def index(self) -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": (
                "REST API for GDP Economic Shock prediction. "
                "Predicts whether a country will experience a GDP shock based on macroeconomic indicators."
            ),
            "docs_url": "/docs",
            "redoc_url": "/redoc",
        }

    def health(self) -> dict:
        if not self._loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        return {"status": "ok", "model_loaded": True}

    def info(self) -> dict:
        if not self._loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        return {
            "model_type": self._payload.get("best_model", "unknown"),
            "sampling_strategy": self._payload.get("best_strategy", "unknown"),
            "optimal_threshold": self.threshold,
            "features": self.feature_names,
            "metrics": self._payload.get("test_metrics", {}),
            "training_date": self._payload.get("training_date", "unknown"),
            "version": settings.app_version,
        }

    def predict(self, request: PredictRequest) -> PredictResponse:
        if not self._loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")

        df = pd.DataFrame([request.model_dump()])
        try:
            prob = float(self.pipeline.predict_proba(df)[:, 1][0])
        except Exception as exc:
            logger.error(f"Prediction error: {exc}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

        prediction = "choc" if prob >= self.threshold else "normal"
        return PredictResponse(
            prediction=prediction,
            probability=round(prob, 4),
            threshold=self.threshold,
            confidence=_confidence_label(prob, self.threshold),
        )

    async def batch_predict(self, file: UploadFile) -> StreamingResponse:
        if not self._loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")

        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are accepted")

        try:
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}")

        # Validate required columns
        missing = [c for c in self.feature_names if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns in CSV: {missing}"
            )

        try:
            probs = self.pipeline.predict_proba(df[self.feature_names])[:, 1]
        except Exception as exc:
            logger.error(f"Batch prediction error: {exc}")
            raise HTTPException(status_code=500, detail=f"Batch prediction failed: {exc}")

        df["probability"] = np.round(probs, 4)
        df["prediction"] = np.where(probs >= self.threshold, "choc", "normal")
        df["threshold"] = self.threshold
        df["confidence"] = [_confidence_label(p, self.threshold) for p in probs]

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=predictions.csv"},
        )


# Singleton — loaded once at startup
_model_service_instance = ModelService()