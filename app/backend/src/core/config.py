from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql://postgres:admin2255@localhost:5433/fcms"

    # Model
    model_path: str = "modeling/models/final_model.joblib"

    # API
    app_name: str = "GDP Shock Prediction API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Upload paths
    upload_dir: str = "uploads"
    output_dir: str = "outputs"


settings = Settings()