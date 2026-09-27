"""Application configuration settings."""

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
    POSTGRES_DB: str = "assetcare_db"
    POSTGRES_PORT: int = 5433
    DATABASE_URL: str = (
        "postgresql+psycopg2://assetcare:assetcare_secret@db:5432/assetcare_db"
    )

    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins formatted as a list of strings."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
