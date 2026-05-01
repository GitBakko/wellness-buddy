"""Weight schemas — minimal placeholders. Plan 07 owns real impl."""

from __future__ import annotations

from pydantic import BaseModel


class WeightLogIn(BaseModel):
    date: str  # ISO date
    weight_kg: float
    notes: str | None = None


class WeightLogOut(BaseModel):
    id: str
    date: str
    weight_kg: float
    notes: str | None = None
