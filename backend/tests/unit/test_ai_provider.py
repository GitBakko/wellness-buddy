"""AI provider unit tests — T-AI-01, AI-01..AI-04, AI-07.

Confirms:
- NullProvider IS-A AIProvider
- NullProvider.is_available is False
- Each AI method raises HTTPException(501) with the Italian envelope
- Factory returns NullProvider when settings.AI_PROVIDER == 'null'
- Factory raises ValueError on unknown AI_PROVIDER
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.ai.base import AIProvider
from app.ai.null_provider import NullProvider


def test_null_provider_is_aiprovider() -> None:
    assert issubclass(NullProvider, AIProvider)


def test_null_provider_not_available() -> None:
    assert NullProvider().is_available is False


@pytest.mark.asyncio
async def test_null_provider_meal_suggestion_raises_501_italian() -> None:
    with pytest.raises(HTTPException) as exc:
        await NullProvider().generate_meal_suggestion()
    assert exc.value.status_code == 501
    assert exc.value.detail == {"detail": "AI non disponibile", "code": "ai_unavailable"}


@pytest.mark.asyncio
async def test_null_provider_week_analysis_raises_501_italian() -> None:
    with pytest.raises(HTTPException) as exc:
        await NullProvider().analyze_week_progress()
    assert exc.value.status_code == 501
    assert exc.value.detail == {"detail": "AI non disponibile", "code": "ai_unavailable"}


@pytest.mark.asyncio
async def test_null_provider_shopping_tips_raises_501_italian() -> None:
    with pytest.raises(HTTPException) as exc:
        await NullProvider().generate_shopping_tips()
    assert exc.value.status_code == 501
    assert exc.value.detail == {"detail": "AI non disponibile", "code": "ai_unavailable"}


@pytest.mark.asyncio
async def test_null_provider_chat_raises_501_italian() -> None:
    with pytest.raises(HTTPException) as exc:
        await NullProvider().chat()
    assert exc.value.status_code == 501
    assert exc.value.detail == {"detail": "AI non disponibile", "code": "ai_unavailable"}


def test_factory_returns_null_provider_when_env_null(monkeypatch: pytest.MonkeyPatch) -> None:
    """Factory returns NullProvider for AI_PROVIDER='null'."""
    from app.ai import factory as fac

    monkeypatch.setattr(fac.settings, "AI_PROVIDER", "null")
    provider = fac.build_provider()
    assert type(provider).__name__ == "NullProvider"
    assert isinstance(provider, AIProvider)


def test_factory_raises_for_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Factory raises ValueError on unknown AI_PROVIDER (boot defense)."""
    from app.ai import factory as fac

    monkeypatch.setattr(fac.settings, "AI_PROVIDER", "weird-unknown")
    with pytest.raises(ValueError, match="Unknown AI_PROVIDER"):
        fac.build_provider()
