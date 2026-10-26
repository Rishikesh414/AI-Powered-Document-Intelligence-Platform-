from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # LLM Configuration
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODE: str = "gemini"  # "gemini" or "mock"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "*"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_MIME_TYPES: str = "application/pdf,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    # Database Configuration (PostgreSQL / SQLite fallback)
    # e.g., postgresql://user:password@localhost:5432/docuintel
    DATABASE_URL: Optional[str] = None

    # File System Storage (Backend Upload Directory)
    UPLOAD_DIR: str = "uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
