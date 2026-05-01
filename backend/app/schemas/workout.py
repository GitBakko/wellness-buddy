"""Workout log schemas — Plan 07.

Source: WORK-01, WORK-02. `trained=False` is valid with no other fields (user just
records "non ho allenato oggi").
"""

from __future__ import annotations

from datetime import date as date_t

from pydantic import BaseModel, ConfigDict, Field


class WorkoutLogIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date_t
    trained: bool
    duration_min: int | None = Field(default=None, ge=0, le=24 * 60)
    calories_burned: int | None = Field(default=None, ge=0, le=10_000)
    workout_type: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=4_000)


class WorkoutLogPatch(BaseModel):
    """Partial update — every field optional. `date` immutable (delete + recreate)."""

    model_config = ConfigDict(extra="forbid")

    trained: bool | None = None
    duration_min: int | None = Field(default=None, ge=0, le=24 * 60)
    calories_burned: int | None = Field(default=None, ge=0, le=10_000)
    workout_type: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=4_000)
    date: date_t | None = None  # echoed in symmetry but ignored


class WorkoutLogOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    date: date_t
    trained: bool
    duration_min: int | None = None
    calories_burned: int | None = None
    workout_type: str | None = None
    notes: str | None = None
