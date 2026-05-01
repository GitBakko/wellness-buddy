"""Pydantic-settings application config.

NOTE (worktree race): Plan 02a is the canonical owner of this file — this is a
minimal stub written by Plan 02b so the AI factory can read AI_PROVIDER cleanly.
Plan 02a's full Settings (DATABASE_URL, SECRET_KEY, etc.) will replace this on
Wave 2 merge. Tests only exercise AI_PROVIDER so the surface is intentionally narrow.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Subset of application settings consumed by Plan 02b's AI layer."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Plan 02a will tighten to strict; here we tolerate extras
        case_sensitive=False,
    )

    # AI provider selector — D-31, D-32. Sprint 1: only "null" supported.
    AI_PROVIDER: str = "null"


settings = Settings()
