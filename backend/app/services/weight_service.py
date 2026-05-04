"""Weight log service — Plan 07.

Source: WEIGHT-01, WEIGHT-02, T-API-03 (cross-user 404 not 403 — V13).

Behavior:
  * `upsert_weight` — POST /api/weight semantics (UNIQUE(user_id, date)).
    On conflict, update existing row's weight_kg (CONV-13 LWW).
  * `list_weights` — current user only, desc by date.
  * `update_weight` — scoped WHERE id == X AND user_id == current; 404 otherwise.
  * `delete_weight` — same scope.
"""

from __future__ import annotations

from datetime import date as date_t
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.weight import WeightLog

_MSG_NOT_FOUND = "Pesata non trovata."


async def upsert_weight(
    session: AsyncSession,
    *,
    user_id: UUID,
    on_date: date_t,
    weight_kg: Decimal,
) -> WeightLog:
    """Insert-or-update by (user_id, date)."""
    existing = (
        await session.scalars(
            select(WeightLog).where(WeightLog.user_id == user_id, WeightLog.date == on_date)
        )
    ).first()
    if existing:
        existing.weight_kg = weight_kg
        await session.commit()
        await session.refresh(existing)
        return existing

    row = WeightLog(user_id=user_id, date=on_date, weight_kg=weight_kg)
    session.add(row)
    try:
        await session.commit()
        await session.refresh(row)
        return row
    except IntegrityError:
        # Race condition: another request just inserted; retry as update.
        await session.rollback()
        existing = (
            await session.scalars(
                select(WeightLog).where(WeightLog.user_id == user_id, WeightLog.date == on_date)
            )
        ).first()
        if not existing:
            raise
        existing.weight_kg = weight_kg
        await session.commit()
        await session.refresh(existing)
        return existing


async def list_weights(session: AsyncSession, *, user_id: UUID) -> list[WeightLog]:
    """User-scoped list, newest first."""
    rows = (
        await session.scalars(
            select(WeightLog).where(WeightLog.user_id == user_id).order_by(WeightLog.date.desc())
        )
    ).all()
    return list(rows)


async def update_weight(
    session: AsyncSession,
    *,
    user_id: UUID,
    weight_id: UUID,
    weight_kg: Decimal,
) -> WeightLog:
    row = (
        await session.scalars(
            select(WeightLog).where(WeightLog.id == weight_id, WeightLog.user_id == user_id)
        )
    ).first()
    if not row:
        # V13 — same envelope as truly-missing; never reveal cross-user existence.
        raise AppException(404, _MSG_NOT_FOUND, "not_found")
    row.weight_kg = weight_kg
    await session.commit()
    await session.refresh(row)
    return row


async def delete_weight(session: AsyncSession, *, user_id: UUID, weight_id: UUID) -> None:
    row = (
        await session.scalars(
            select(WeightLog).where(WeightLog.id == weight_id, WeightLog.user_id == user_id)
        )
    ).first()
    if not row:
        raise AppException(404, _MSG_NOT_FOUND, "not_found")
    await session.delete(row)
    await session.commit()
