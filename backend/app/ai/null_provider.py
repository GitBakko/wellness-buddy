"""NullProvider — raises HTTPException 501 Italian.

Sources: AI-04, AI-07, RESEARCH Pattern 11, T-AI-01.

The NullProvider is the Sprint 1 default and never emits sensitive context. All
abstract methods raise the same hardcoded Italian envelope so frontend can render
the locked AIWidget placeholder ("AI non disponibile — coming soon").
"""

from __future__ import annotations

from fastapi import HTTPException

from app.ai.base import AIProvider

_DETAIL: dict[str, str] = {"detail": "AI non disponibile", "code": "ai_unavailable"}


class NullProvider(AIProvider):
    """Sprint 1 placeholder. Raises 501 with Italian envelope on every call."""

    async def generate_meal_suggestion(self, **kwargs: object) -> str:
        raise HTTPException(status_code=501, detail=_DETAIL)

    async def analyze_week_progress(self, **kwargs: object) -> str:
        raise HTTPException(status_code=501, detail=_DETAIL)

    async def generate_shopping_tips(self, **kwargs: object) -> str:
        raise HTTPException(status_code=501, detail=_DETAIL)

    async def chat(self, **kwargs: object) -> str:
        raise HTTPException(status_code=501, detail=_DETAIL)

    @property
    def is_available(self) -> bool:
        return False
