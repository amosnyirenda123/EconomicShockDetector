import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from service.model_service import _model_service_instance
from api import model_api, user_api
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Loading ML model…")
    _model_service_instance.load()
    logger.info("Model ready. Starting API.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "GDP Economic Shock Prediction API. "
        "Predicts whether a country-year observation will experience a GDP shock "
        "based on macroeconomic indicators. "
        "See `/docs` for interactive Swagger UI."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(model_api.router, tags=["model"])
app.include_router(user_api.router)