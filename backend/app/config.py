"""Application configuration using pydantic-settings for environment variable management."""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings

# Resolve .env from backend/ or parent (project root)
_HERE = Path(__file__).parent.parent  # backend/
_ENV_FILE = str(_HERE / ".env") if (_HERE / ".env").exists() else str(_HERE.parent / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Veridian"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./veridian.db"

    # JWT Authentication
    SECRET_KEY: str = "dev-secret-key-change-in-production-9f8a7b6c5d4e3f2a1b0c"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # AI Models
    MODEL_DIR: str = "./models"
    SMS_MODEL_PATH: str = "./models/sms_model.pkl"
    EMAIL_MODEL_PATH: str = "./models/email_model.pkl"
    URL_MODEL_PATH: str = "./models/url_model.pkl"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = {
        "env_file": _ENV_FILE,
        "case_sensitive": True,
        "extra": "ignore",   # Ignore POSTGRES_USER, POSTGRES_PASSWORD, etc.
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings singleton."""
    return Settings()
