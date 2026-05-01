"""FastAPI dependency providers.

NOTE (worktree race): Plan 02a is the canonical owner of this file — this is a
minimal stub by Plan 02b so the AI router can wire `Depends(get_ai_provider)`
and `Depends(get_current_user)`. Plan 02a will replace `get_current_user` with
the real JWT-backed implementation; here it raises 501 with the AUTH-12 envelope
so stub-mode tests still see a consistent {detail, code} shape.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from app.ai.base import AIProvider


def get_ai_provider(request: Request) -> AIProvider:
    """Return the AIProvider singleton bound at lifespan startup (D-32)."""
    provider = getattr(request.app.state, "ai_provider", None)
    if provider is None:
        # Should be impossible in well-formed boot — surface clearly if it ever happens.
        raise HTTPException(
            status_code=500,
            detail={"detail": "AI provider non inizializzato", "code": "ai_provider_missing"},
        )
    return provider


def get_current_user() -> dict[str, str]:
    """Stub auth dependency — Plan 03 replaces with real JWT validation.

    Phase 1 stub: returns 501 with AUTH-12 envelope so the API surface is
    auth-gated by default. Plan 03's implementation will validate access tokens
    and return the User model.
    """
    raise HTTPException(
        status_code=501,
        detail={"detail": "Autenticazione non ancora disponibile", "code": "auth_not_implemented"},
    )
