"""Family share toggle service (FAM-02, FAM-03, D-15).

Owner-only mutation: ``toggle_share`` looks up the variant row by
``(variant_id, user_id == current_user.id)``. A non-owner attempt returns
404 with ``not_found`` envelope (V13 — same shape as truly-missing).

Visibility is constrained to the locked enum values ``private`` |
``group_shared``. Anything else raises 400 ``validation_error`` (already
caught by the Pydantic body in :mod:`app.schemas.family`, but the service
layer double-checks so callers can use it directly without going through
the HTTP boundary).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant


async def toggle_share(
    session: AsyncSession,
    *,
    user: User,
    variant_id: UUID,
    visibility: str,
) -> WeeklyPlanVariant:
    """PATCH /api/family/share/{variant_id} — owner-only visibility toggle.

    Returns the refreshed variant row on success. Side-effect: bumps
    ``version`` so concurrent edits in another tab will surface the LWW
    409 toast (CONV-13).
    """
    if visibility not in ("private", "group_shared"):
        raise AppException(400, "Visibilità non valida.", "validation_error")

    row = (
        await session.scalars(
            select(WeeklyPlanVariant).where(
                WeeklyPlanVariant.id == variant_id,
                WeeklyPlanVariant.user_id == user.id,
            )
        )
    ).first()
    if not row:
        # V13 — same envelope as non-existent. Never reveal "you're not the
        # owner" because that leaks the variant's existence.
        raise AppException(404, "Risorsa non trovata.", "not_found")

    row.visibility = Visibility(visibility)
    row.version = row.version + 1
    await session.commit()
    await session.refresh(row)
    return row
