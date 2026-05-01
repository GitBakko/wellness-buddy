"""FastAPI DI helpers.

Plan 03 replaces 02a's stub `get_current_user` with the real JWT-based dependency.
Routes that depend on it (Plan 03+ /me, /invite, plus future Plan 04/07 user-scoped
endpoints) extract the access token from `Authorization: Bearer ...`, decode + verify
its signature/exp/type, then fetch the User by `sub` claim.

`get_ai_provider` (Plan 02b) reads `request.app.state.ai_provider`.
`require_admin` gates by `user.role == 'admin'`.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import AppException
from app.core.security import decode_token
from app.models.user import User

# Italian copy lifted into backend errors per AUTH-12 envelope.
_MSG_SESSION_EXPIRED = "Sessione scaduta dopo 7 giorni di inattività. Accedi di nuovo."


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_session),
) -> User:
    """Extract + verify the access JWT from the Authorization header, return the user.

    Raises AppException with AUTH-12 envelope on any failure (no header, malformed,
    wrong type, expired, user gone). Frontend code maps these codes to italian copy
    via `copy.it.ts`.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppException(401, _MSG_SESSION_EXPIRED, "no_token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception as e:
        raise AppException(401, _MSG_SESSION_EXPIRED, "expired") from e
    if payload.get("type") != "access":
        raise AppException(401, "Token non valido", "invalid_token")
    user_id = UUID(payload["sub"])
    user = (
        await session.scalars(select(User).where(User.id == user_id))
    ).first()
    if not user:
        raise AppException(401, "Utente non trovato", "user_not_found")
    return user


def get_ai_provider(request: Request) -> object:
    """Return the AI provider singleton bound by Plan 02b's lifespan extension.

    Raises 503 if the provider was never bound (defensive — should not happen post-02b).
    """
    provider = getattr(request.app.state, "ai_provider", None)
    if provider is None:
        raise AppException(503, "ai_provider_unbound", "ai_provider_unbound")
    return provider


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Authorization gate: pass through admins, 403 with `forbidden` envelope otherwise."""
    if getattr(user, "role", None) != "admin":
        raise AppException(403, "Non hai accesso a questa sezione.", "forbidden")
    return user
