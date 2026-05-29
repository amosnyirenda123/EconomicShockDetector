from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CURRENT_DIR = os.getcwd()
MODEL_PATH = PROJECT_ROOT / "modeling" / "models" / "final_model.joblib"
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
print(MODEL_PATH)
ENV_FILE_PATH = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    # Database
    database_url: str

    # Model
    model_path: str = str(MODEL_PATH)

    # API
    app_name: str = "GDP Shock Prediction API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Upload paths
    upload_dir: str = "uploads"
    output_dir: str = "outputs"


settings = Settings()