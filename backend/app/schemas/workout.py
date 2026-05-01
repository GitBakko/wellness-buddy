"""Workout schemas — minimal placeholders. Plan 07 owns real impl."""

from __future__ import annotations

from pydantic import BaseModel


class WorkoutLogIn(BaseModel):
    date: str  # ISO date
    type: str
    duration_min: int
    notes: str | None = None


class WorkoutLogOut(BaseModel):
    id: str
    date: str
    type: str
    duration_min: int
    notes: str | None = None
