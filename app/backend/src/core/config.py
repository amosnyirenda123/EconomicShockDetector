from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "modeling" / "models" / "final_model.joblib"
PREPROCESSOR_PATH = PROJECT_ROOT / "modeling" / "models" / "preprocessor.joblib"
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BACKEND_DIR / ".env"
ARTIFACTS_DIR = PROJECT_ROOT / "modeling" / "models"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    # Database
    database_url: str

    # Model
    model_path: str = str(MODEL_PATH)

    # Preprocessor
    preprocessor_path: str = str(PREPROCESSOR_PATH)

    # API
    app_name: str = "GDP Shock Prediction API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Upload paths
    upload_dir: str = "uploads"
    output_dir: str = "outputs"


settings = Settings()