"""Workout router — Plan 07 implementation (replaces 02b's 501 stub).

Endpoints (all auth-gated):
  * POST   /api/workout                  — upsert by (user_id, date)
  * GET    /api/workout?start=&end=      — current user, optional inclusive date range
  * PATCH  /api/workout/{workout_id}     — partial update (cross-user 404)
  * DELETE /api/workout/{workout_id}     — remove (cross-user 404)

Source: WORK-01, WORK-02, T-API-03, V13.
"""

from __future__ import annotations

from datetime import date as date_t
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.workout import WorkoutLogIn, WorkoutLogOut, WorkoutLogPatch
from app.services import workout_service

router = APIRouter(prefix="/api/workout", tags=["workout"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WorkoutLogOut)
async def post_workout(
    body: WorkoutLogIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorkoutLogOut:
    row = await workout_service.upsert_workout(
        session,
        user_id=user.id,
        on_date=body.date,
        trained=body.trained,
        duration_min=body.duration_min,
        calories_burned=body.calories_burned,
        workout_type=body.workout_type,
        notes=body.notes,
    )
    return WorkoutLogOut(
        id=str(row.id),
        date=row.date,
        trained=row.trained,
        duration_min=row.duration_min,
        calories_burned=row.calories_burned,
        workout_type=row.workout_type,
        notes=row.notes,
    )


@router.get("", response_model=list[WorkoutLogOut])
async def list_workouts(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    start: date_t | None = Query(default=None),
    end: date_t | None = Query(default=None),
) -> list[WorkoutLogOut]:
    rows = await workout_service.list_workouts(session, user_id=user.id, start=start, end=end)
    return [
        WorkoutLogOut(
            id=str(r.id),
            date=r.date,
            trained=r.trained,
            duration_min=r.duration_min,
            calories_burned=r.calories_burned,
            workout_type=r.workout_type,
            notes=r.notes,
        )
        for r in rows
    ]


@router.patch("/{workout_id}", response_model=WorkoutLogOut)
async def patch_workout(
    workout_id: UUID,
    body: WorkoutLogPatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorkoutLogOut:
    fields = body.model_dump(exclude_unset=True, exclude={"date"})
    row = await workout_service.update_workout(
        session,
        user_id=user.id,
        workout_id=workout_id,
        fields=fields,
    )
    return WorkoutLogOut(
        id=str(row.id),
        date=row.date,
        trained=row.trained,
        duration_min=row.duration_min,
        calories_burned=row.calories_burned,
        workout_type=row.workout_type,
        notes=row.notes,
    )


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await workout_service.delete_workout(session, user_id=user.id, workout_id=workout_id)
