"""AI router — endpoints exist Phase 1, return 501 via NullProvider (AI-04, AI-07).

Sources: AI-01..AI-04, AI-07, RESEARCH Pattern 11, T-AI-01.

The four real endpoints (`/meal-suggestion`, `/week-analysis`, `/shopping-tips`,
`/chat`) wire through `Depends(get_ai_provider)`. With NullProvider bound at
lifespan startup, all four bubble HTTPException(501) with the Italian envelope
`{detail: "AI non disponibile", code: "ai_unavailable"}`.

The test-only `/_provider_probe` endpoint bypasses auth so CI can confirm the
NullProvider class is wired correctly. It is hidden from the OpenAPI schema
(`include_in_schema=False`) and will be removed in Sprint 5.

We use PEP 593 `Annotated[..., Depends(...)]` to satisfy ruff B008 (no function
calls in argument defaults). The wire-format is identical to the older default-
argument style — FastAPI inspects both equivalently.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.ai.base import AIProvider
from app.core.deps import get_ai_provider, get_current_user

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Type aliases that carry the Depends marker (PEP 593) — keeps endpoint
# signatures readable while satisfying ruff B008.
CurrentUser = Annotated[dict[str, str], Depends(get_current_user)]
AIDep = Annotated[AIProvider, Depends(get_ai_provider)]


@router.get("/_provider_probe", include_in_schema=False)
async def _provider_probe(request: Request) -> dict[str, object]:
    """Test-only: confirm the active AIProvider class without going through auth."""
    ai: AIProvider = get_ai_provider(request)
    return {"provider": type(ai).__name__, "is_available": ai.is_available}


@router.post("/meal-suggestion")
async def meal_suggestion(user: CurrentUser, ai: AIDep) -> dict[str, str]:
    return {"suggestion": await ai.generate_meal_suggestion()}


@router.post("/week-analysis")
async def week_analysis(user: CurrentUser, ai: AIDep) -> dict[str, str]:
    return {"analysis": await ai.analyze_week_progress()}


@router.post("/shopping-tips")
async def shopping_tips(user: CurrentUser, ai: AIDep) -> dict[str, str]:
    return {"tips": await ai.generate_shopping_tips()}


@router.post("/chat")
async def chat(user: CurrentUser, ai: AIDep) -> dict[str, str]:
    return {"response": await ai.chat()}
