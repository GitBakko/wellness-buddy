"""Strict Pydantic v2 schema downstream of tolerant parser.

Source: PLAN-06, RESEARCH Pattern 10, T-PARSE-03 (crafted JSON bypass downstream).

`extra='forbid'` rejects unknown keys at validation — the tolerant parser produces
a dict, this schema is the contract gate before persistence and downstream consumers
(/today, /shopping, /admin) can rely on the shape.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PersonalData(BaseModel):
    """Section: DATI PERSONALI."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    age: int | None = None
    current_weight_kg: float | None = None
    target_weight_kg: float | None = None


class Macros(BaseModel):
    """Section: CALCOLO CALORICO E MACRO TARGET (also embedded in MealOption)."""

    model_config = ConfigDict(extra="forbid")

    kcal: int = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0


class Ingredient(BaseModel):
    """Phase 1 unused — placeholder for Phase 2 deeper meal parsing."""

    model_config = ConfigDict(extra="forbid")

    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None


class MealOption(BaseModel):
    """A single meal alternative (e.g. `### Opzione A`)."""

    model_config = ConfigDict(extra="forbid")

    key: str
    title: str
    ingredients: list[Ingredient] = Field(default_factory=list)
    macros: Macros = Field(default_factory=Macros)


class PlanParsedSchema(BaseModel):
    """Aggregator. Every field optional/defaulted so partial plans still validate
    and downstream consumers can defensively render."""

    model_config = ConfigDict(extra="forbid")

    personal_data: PersonalData | None = None
    macro_target: Macros = Field(default_factory=Macros)
    daily_structure: list[dict] = Field(default_factory=list)
    breakfast: MealOption | None = None
    lunches: dict[str, list[MealOption]] = Field(default_factory=dict)
    dinners: dict[str, list[MealOption]] = Field(default_factory=dict)
    snacks: list[MealOption] = Field(default_factory=list)
    supplements: list[dict] = Field(default_factory=list)
    weight_projection: list[dict] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
