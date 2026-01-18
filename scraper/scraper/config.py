"""Scraper configuration."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


class Settings(BaseSettings):
    """Scraper settings."""

    DATABASE_URL: str = Field(alias="SCRAPER_DATABASE_URL")
    NYC_OPEN_DATA_APP_TOKEN: str = ""
    USER_AGENT: str = "HopePlatform/1.0"

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env (needed for backend imports)
        populate_by_name=True  # Allow using field name or alias
    )


settings = Settings()
