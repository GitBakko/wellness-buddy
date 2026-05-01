"""Workout log service — Plan 07.

Source: WORK-01, WORK-02, T-API-03, V13. Workout is ALWAYS private (CONV-14).

Behavior:
  * `upsert_workout` — POST /api/workout semantics (one entry per user_id+date).
    Phase 1 allows updating the existing row when re-posting same date.
  * `list_workouts` — optional date-range filter. Current user only.
  * `update_workout` / `delete_workout` — scoped + 404 on cross-user.
"""

from __future__ import annotations

from datetime import date as date_t
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.workout import WorkoutLog


_MSG_NOT_FOUND = "Allenamento non trovato."


async def upsert_workout(
    session: AsyncSession,
    *,
    user_id: UUID,
    on_date: date_t,
    trained: bool,
    duration_min: int | None,
    calories_burned: int | None,
    workout_type: str | None,
    notes: str | None,
) -> WorkoutLog:
    """Insert-or-update by (user_id, date). The model has no UNIQUE constraint, so we
    do a manual lookup; if another row exists for the same date, update it."""
    existing = (
        await session.scalars(
            select(WorkoutLog).where(
                WorkoutLog.user_id == user_id, WorkoutLog.date == on_date
            )
        )
    ).first()
    if existing:
        existing.trained = trained
        existing.duration_min = duration_min
        existing.calories_burned = calories_burned
        existing.workout_type = workout_type
        existing.notes = notes
        await session.commit()
        await session.refresh(existing)
        return existing

    row = WorkoutLog(
        user_id=user_id,
        date=on_date,
        trained=trained,
        duration_min=duration_min,
        calories_burned=calories_burned,
        workout_type=workout_type,
        notes=notes,
    )
    session.add(row)
    try:
        await session.commit()
        await session.refresh(row)
        return row
    except IntegrityError:
        await session.rollback()
        raise


async def list_workouts(
    session: AsyncSession,
    *,
    user_id: UUID,
    start: date_t | None = None,
    end: date_t | None = None,
) -> list[WorkoutLog]:
    """User-scoped list, optional [start, end] inclusive range. Newest first."""
    stmt = (
        select(WorkoutLog)
        .where(WorkoutLog.user_id == user_id)
        .order_by(WorkoutLog.date.desc())
    )
    if start is not None:
        stmt = stmt.where(WorkoutLog.date >= start)
    if end is not None:
        stmt = stmt.where(WorkoutLog.date <= end)
    rows = (await session.scalars(stmt)).all()
    return list(rows)


async def update_workout(
    session: AsyncSession,
    *,
    user_id: UUID,
    workout_id: UUID,
    fields: dict,
) -> WorkoutLog:
    """Patch only provided fields. Cross-user → 404 (V13)."""
    row = (
        await session.scalars(
            select(WorkoutLog).where(
                WorkoutLog.id == workout_id, WorkoutLog.user_id == user_id
            )
        )
    ).first()
    if not row:
        raise AppException(404, _MSG_NOT_FOUND, "not_found")

    # Whitelist mutable fields. `date` is immutable (delete + recreate per spec).
    allowed = {
        "trained",
        "duration_min",
        "calories_burned",
        "workout_type",
        "notes",
    }
    for key, value in fields.items():
        if key in allowed and value is not None:
            setattr(row, key, value)

    await session.commit()
    await session.refresh(row)
    return row


async def delete_workout(
    session: AsyncSession, *, user_id: UUID, workout_id: UUID
) -> None:
    row = (
        await session.scalars(
            select(WorkoutLog).where(
                WorkoutLog.id == workout_id, WorkoutLog.user_id == user_id
            )
        )
    ).first()
    if not row:
        raise AppException(404, _MSG_NOT_FOUND, "not_found")
    await session.delete(row)
    await session.commit()
