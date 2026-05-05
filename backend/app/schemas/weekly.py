"""Pydantic schemas for /api/weekly endpoints (WEEK-01..05, FAM-04).

The shape is consumed by `frontend/src/services/weekly.ts::WeeklyResponse` —
keep them in sync via interface mirror (no generated bindings Phase 2).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MealOptionPayload(BaseModel):
    """Plan 02-04 — single variant option offered for a (day, meal_type) cell.

    Surfaces the title + key + macro preview the frontend needs to render the
    per-day variant selector. Grid-format plans usually have 1-3 options per
    cell; subheading-format plans surface week-level options once per day.
    """

    model_config = ConfigDict(extra="forbid")

    key: str
    title: str
    macros: dict[str, Any] = Field(default_factory=dict)


class MealEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slot: str
    title: str
    variant_key: str
    visibility: str  # 'private' | 'group_shared'
    version: int
    updated_at: str | None
    completed: bool
    owner_user_id: str
    macros: dict[str, Any] = Field(default_factory=dict)
    ingredients: list[Any] = Field(default_factory=list)
    # Plan 02-04 — per-day variant options the user can pick between for this
    # (day_of_week, slot). Empty list when the slot has no alternatives (e.g.
    # breakfast — single dict in parsed_json).
    options: list[MealOptionPayload] = Field(default_factory=list)
    # Plan 02-05 — temporal slot for snacks ('afternoon' | 'evening' | None).
    # weekly_service emits TWO snack entries per day when the plan has both a
    # SPUNTINO POMERIGGIO and a SPUNTINO SERALE section. Frontend renders
    # afternoon BEFORE dinner and evening AFTER dinner (matches /today order).
    snack_slot: str | None = None


class WeeklyDay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    day_of_week: int
    meals: list[MealEntry]


class WeeklyTotals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float


class WeeklyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_start: str
    days: list[WeeklyDay]
    totals: WeeklyTotals


class WeeklySummaryDay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float


class WeeklySummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_start: str
    kcal_total: float
    protein_g: float
    carbs_g: float
    fat_g: float
    days: list[WeeklySummaryDay]


class PatchVariantPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    day_of_week: int = Field(ge=0, le=6)
    meal_type: str  # 'breakfast' | 'lunch' | 'dinner' | 'snack'
    variant_key: str  # 'A' | 'B' | 'pasta' | 'special' (mapped to UI labels via copy.it.ts)
    visibility: str | None = None  # optional override


class VariantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    week_start: str
    day_of_week: int
    meal_type: str
    variant_key: str
    visibility: str
    version: int
    updated_at: str
    completed: bool
