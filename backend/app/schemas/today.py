"""Today schemas — minimal placeholder. Plan 07 owns real impl."""

from __future__ import annotations

from pydantic import BaseModel


class TodayResponse(BaseModel):
    date: str  # ISO date Europe/Rome
    meals: list[dict[str, object]] = []
    weight_logged: bool = False
    workout_logged: bool = False
