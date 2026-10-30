"""Application configuration settings."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Asset Care API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    POSTGRES_USER: str = "assetcare"
    POSTGRES_PASSWORD: str = "assetcare_secret"
    POSTGRES_HOST: str = "asset_care_db"
    POSTGRES_DB: str = "assetcare_db"
    POSTGRES_PORT: int = 5433
    DATABASE_URL: str | None = None

    CORS_ORIGINS: str = "*"

    @model_validator(mode="after")
    def assemble_database_url(self) -> "Settings":
        """Build DATABASE_URL from POSTGRES_* fields when not explicitly set."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
            )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins formatted as a list of strings."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
