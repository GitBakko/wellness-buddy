"""FastAPI DI helpers.

`get_current_user` is a STUB raising 501 here — Plan 03 (auth) replaces with the
real JWT-based dependency. Routes that depend on it land in Plan 03+ so Phase 1
plans can import the symbol freely.

`get_ai_provider` reads `request.app.state.ai_provider`, which Plan 02b binds in
the lifespan. Until 02b runs, calling this raises a clear error rather than
returning silently None.

`require_admin` gates by `user.role == 'admin'`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, Request

from app.core.exceptions import AppException

if TYPE_CHECKING:
    # Avoid runtime circular import; models pull in db engine which may not be ready
    from app.models.user import User


async def get_current_user() -> User:
    """STUB: real implementation lands in Plan 03 (auth).

    Phase 1 plans (02a) only need the symbol importable so route signatures compile.
    Any route accidentally calling this in Phase 1 returns 501 fast.
    """
    raise AppException(501, "auth_not_implemented", "auth_not_implemented")


def get_ai_provider(request: Request) -> object:
    """Return the AI provider singleton bound by Plan 02b's lifespan extension.

    Raises 503 if the provider was never bound (defensive — should not happen post-02b).
    """
    provider = getattr(request.app.state, "ai_provider", None)
    if provider is None:
        raise AppException(503, "ai_provider_unbound", "ai_provider_unbound")
    return provider


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Authorization gate: pass through admins, 403 everyone else."""
    if getattr(user, "role", None) != "admin":
        raise AppException(403, "admin_required", "admin_required")
    return user
