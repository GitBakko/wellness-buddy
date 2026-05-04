"""WeeklyPlanVariant CRUD + LWW conflict resolution (D-17, FAM-04, WEEK-04).

Pattern: client sends `If-Unmodified-Since: <updated_at ISO>` header derived from
the variant version it last fetched. Server compares to current row.updated_at:
  - match (or row not yet existing): proceed; bump version + updated_at via SQLAlchemy default.
  - mismatch: raise AppException(409, ..., code="version_conflict").

Default visibility (FAM-02): cene/pranzi → GROUP_SHARED, colazione/spuntini → PRIVATE.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant

_MSG_CONFLICT = "Aggiornato da {nome}. Ricarica per vedere l'ultima versione."


def default_visibility_for(meal_type: str) -> Visibility:
    """FAM-02: cene + pranzi default group_shared; colazione + spuntini default private."""
    return Visibility.GROUP_SHARED if meal_type in ("lunch", "dinner") else Visibility.PRIVATE


async def upsert_variant(
    session: AsyncSession,
    *,
    user: User,
    plan_id: UUID,
    week_start: date,
    day_of_week: int,
    meal_type: str,
    variant_key: str,
    visibility: Visibility | None = None,
    if_unmodified_since: datetime | None = None,
) -> WeeklyPlanVariant:
    """Create or update a WeeklyPlanVariant with LWW conflict detection.

    if_unmodified_since: parsed by API layer from `If-Unmodified-Since` header (ISO-8601).
    Returns the persisted row (refreshed). Raises 409 on stale precondition.
    """
    row = (
        await session.scalars(
            select(WeeklyPlanVariant).where(
                WeeklyPlanVariant.user_id == user.id,
                WeeklyPlanVariant.week_start == week_start,
                WeeklyPlanVariant.day_of_week == day_of_week,
                WeeklyPlanVariant.meal_type == meal_type,
            )
        )
    ).first()

    # LWW conflict detection — only when row exists AND client sent a precondition.
    if row is not None and if_unmodified_since is not None:
        if row.updated_at > if_unmodified_since:
            partner = await _conflict_partner_name(session, row=row, current_user=user)
            raise AppException(
                409,
                _MSG_CONFLICT.format(nome=partner or "un familiare"),
                "version_conflict",
            )

    if row is None:
        if visibility is None:
            visibility = default_visibility_for(meal_type)
        row = WeeklyPlanVariant(
            user_id=user.id,
            plan_id=plan_id,
            week_start=week_start,
            day_of_week=day_of_week,
            meal_type=meal_type,
            variant_key=variant_key,
            visibility=visibility,
            version=1,
        )
        session.add(row)
    else:
        row.variant_key = variant_key
        if visibility is not None:
            row.visibility = visibility
        row.version = row.version + 1

    await session.commit()
    await session.refresh(row)
    return row


async def _conflict_partner_name(
    session: AsyncSession, *, row: WeeklyPlanVariant, current_user: User
) -> str | None:
    """Return the username of the row's owner if different from current_user.

    Used for the FAM-05 conflict toast — surfaces "Aggiornato da {nome}" so the
    client can render a partner-aware message. Returns None when the conflict is
    self-vs-self (e.g. two browser tabs of the same user).
    """
    if row.user_id == current_user.id:
        return None
    other = (await session.scalars(select(User).where(User.id == row.user_id))).first()
    return other.username if other else None
