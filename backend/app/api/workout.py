"""Workout router — Plan 02b stub; Plan 07 implements log CRUD."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/workout", tags=["workout"])

_NOT_IMPL = {"detail": "Plan 07 implementa", "code": "not_implemented"}


@router.post("")
async def create_workout() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.get("")
async def list_workouts() -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.patch("/{workout_id}")
async def update_workout(workout_id: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)


@router.delete("/{workout_id}")
async def delete_workout(workout_id: str) -> dict[str, str]:
    raise HTTPException(status_code=501, detail=_NOT_IMPL)
