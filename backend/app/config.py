import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Model Substitution Governance Tracker"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database connection: Defaults to local SQLite if DATABASE_URL is not set
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./governance.db")
    
    # CORS Origins allowed to talk to the backend
    CORS_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:5173",
        "*"
    ]
    
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
