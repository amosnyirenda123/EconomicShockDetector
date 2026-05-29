import logging

from fastapi import APIRouter, Depends, UploadFile, File

from dependencies import get_model_service
from schemas.schemas import PredictRequest, PredictResponse
from service.model_service import ModelService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", summary="Home — API overview and Swagger link")
def index(svc: ModelService = Depends(get_model_service)):
    return svc.index()


@router.get("/health", summary="Health check")
def health(svc: ModelService = Depends(get_model_service)):
    return svc.health()


@router.get("/model/info", summary="Model metadata and performance metrics")
def model_info(svc: ModelService = Depends(get_model_service)):
    return svc.info()


@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Single prediction",
    description=(
        "Receives macroeconomic features for one country-year observation "
        "and returns the predicted class (choc / normal), raw probability, "
        "the applied threshold, and a confidence label."
    ),
)
def predict(
    request: PredictRequest,
    svc: ModelService = Depends(get_model_service),
):
    logger.info("POST /predict called")
    return svc.predict(request)


@router.post(
    "/predict/batch",
    summary="Batch prediction from CSV",
    description=(
        "Upload a CSV file whose columns match the model features. "
        "Returns an enriched CSV with `prediction`, `probability`, `threshold`, "
        "and `confidence` columns appended."
    ),
)
async def batch_predict(
    file: UploadFile = File(..., description="CSV file with model features"),
    svc: ModelService = Depends(get_model_service),
):
    logger.info(f"POST /predict/batch called — file: {file.filename}")
    return await svc.batch_predict(file)