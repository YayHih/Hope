"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8081"]

    # Environment
    ENVIRONMENT: str = "development"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # SMTP Email Configuration
    SMTP_HOST: str = "mail.privateemail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@campuslens.xyz"
    SMTP_PASSWORD: str
    SMTP_FROM: str = "noreply@campuslens.xyz"

    # Google reCAPTCHA v2
    RECAPTCHA_SITE_KEY: str
    RECAPTCHA_SECRET_KEY: str

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env
    )


settings = Settings()
