"""App settings loaded from backend/.env at boot. Fail-fast on missing required values.

Source: D-21 logging, D-24 SECRET_KEY, D-29 pool, D-32 AI provider,
AUTH-12 envelope, V14 CORS no-wildcard.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Strict env-validated settings.

    All required values must be set in `backend/.env` (never committed).
    Missing/invalid values fail-fast — never silently fall back to insecure defaults.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database (D-29)
    DATABASE_URL: str = Field(..., min_length=10)
    SQL_ECHO: bool = False

    # JWT (D-24, AUTH-04, AUTH-05)
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS (validated at boot, never wildcard prod — V14).
    # NoDecode prevents pydantic-settings from JSON-decoding the env value before split_csv runs.
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    # AI provider (D-31, D-32, AI-07)
    AI_PROVIDER: Literal["null", "ollama", "openai", "anthropic"] = "null"

    # Phase 2 — PDF export backend (D-11, D-14, DEP-06).
    # Default 'weasyprint' (D-11 primary). Plan 02-01 7-day GTK3 spike on Windows Server
    # 2019 may flip this to 'reportlab' if 5xx ≥2% over the spike window.
    # Factory `app.services.pdf_export.get_pdf_exporter` reads this value per request.
    PDF_BACKEND: str = Field(
        default="weasyprint",
        description="'weasyprint' (D-11 primary) | 'reportlab' (D-14 fallback)",
    )

    # Operational
    MAX_USERS: int = 100
    ADMIN_EMAIL: str
    LOG_LEVEL: str = "INFO"
    APP_VERSION: str = "0.1.0"
    BUILD_HASH: str = "dev"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_csv(cls, v: object) -> list[str]:
        """Allow comma-separated string in env var, list in test override."""
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return v
        return []

    @field_validator("CORS_ORIGINS")
    @classmethod
    def reject_wildcard(cls, v: list[str]) -> list[str]:
        """V14: never permit wildcard CORS — only explicit allowlist."""
        if "*" in v:
            raise ValueError("CORS_ORIGINS cannot contain wildcard '*' - set explicit allowlist")
        return v


settings = Settings()  # type: ignore[call-arg]
