"""Application Settings.

Uses Pydantic Settings to load from environment variables / .env file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ──────────────────────────────────
    APP_NAME: str = "Eralove API"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Database ─────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://eralove:eralove_dev@localhost:5432/eralove"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # ── Redis ────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ──────────────────────────────────
    JWT_SECRET_KEY: str = "dev-secret-key-change-this-in-production-immediately"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── AWS S3 ───────────────────────────────
    AWS_S3_BUCKET: str = "eralove-media"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: str | None = "http://localhost:9000"
    S3_PRESIGN_EXPIRY: int = 3600

    # ── Claude AI ────────────────────────────
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

    # ── OAuth ────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # ── Email ────────────────────────────────
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@eralove.com"

    # ── CORS ─────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def is_dev(self) -> bool:
        """Check if running in development mode."""
        return self.DEBUG


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
