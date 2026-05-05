"""Today aggregator schemas — Plan 07.

Source: TODAY-01..TODAY-08, UI-SPEC §6.4 + §7.2.
The shape is consumed by `frontend/src/services/today.ts::TodayResponse` —
keep them in sync via interface mirror (no generated bindings Phase 1).
"""

from __future__ import annotations

from datetime import date as date_t
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MealMacro(BaseModel):
    """Per-meal macros, ints/floats matching `PlanParsedSchema.Macros`."""

    model_config = ConfigDict(extra="forbid")

    kcal: int = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0


class MealIngredient(BaseModel):
    """Plan 02-04 gap-closure — single ingredient line shown under MealCard title.

    Carries free-form `name` (e.g. "200 g salmone al forno") and optional
    `quantity` for legacy ingredient-table plans. Real grid plans encode the
    quantity inline in the name; quantity stays None.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    quantity: str | None = None


class MealEntry(BaseModel):
    """One meal slot for today — emitted from the active plan's parsed_json."""

    model_config = ConfigDict(extra="forbid")

    meal_type: str  # 'breakfast' | 'lunch' | 'dinner' | 'snack'
    variant_key: str  # 'A' | 'B' | 'pasta' | 'default' | snack key
    title: str
    macros: MealMacro = Field(default_factory=MealMacro)
    completed: bool = False
    # Plan 01-09 — optional Lifesum-style photo URL passed through from parsed_json.
    # Phase 1: usually None (parser only extracts when `**Foto:** <url>` line present).
    # Frontend MealCard renders gradient placeholder when null.
    photo_url: str | None = Field(default=None, max_length=500)
    # Plan 02-04 gap-closure — composition list shown on /today MealCard.
    # Empty when the meal has no parsed ingredients (legacy plans without
    # tables AND without grid cells).
    ingredients: list[MealIngredient] = Field(default_factory=list)
    # Plan 02-05 carousel — temporal slot for snacks ('afternoon' | 'evening').
    # Frontend groups snack alternatives by slot so the user swipes between
    # Opzione A/B/C/D in pomeriggio and Alternativa 1/2/3 in serale separately.
    # None for non-snack meals (breakfast/lunch/dinner).
    slot: str | None = None


class TodayWeight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    weight_kg: Decimal


class TodayWorkout(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    trained: bool
    duration_min: int | None = None
    calories_burned: int | None = None
    workout_type: str | None = None
    notes: str | None = None


class TodayResponse(BaseModel):
    """Aggregator payload for `/today` page — single round-trip."""

    model_config = ConfigDict(extra="forbid")

    date: date_t
    day_of_week: int  # 0=Monday..6=Sunday
    greeting_period: str  # 'morning'|'afternoon'|'evening'|'night'
    meals: list[MealEntry] = Field(default_factory=list)
    weight_today: TodayWeight | None = None
    workout_today: TodayWorkout | None = None
    # Plan 02-04 gap-closure — daily macro target from active plan.
    # Frontend uses these as the MacroRing target so the rings show partial
    # fill instead of "100% full" when consumed sums to 0 (no meals completed).
    # All zero when no active plan or plan has no macro_target section.
    macro_target: MealMacro = Field(default_factory=MealMacro)


class MealCompleteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meal_type: str
    completed: bool
    version: int
