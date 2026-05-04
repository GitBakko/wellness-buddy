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
    """Per-row entry parsed from a meal ingredient table.

    `quantity` is kept as a free-form string ("270 ml", "8-10 g", "1 tazzina")
    because real plans use ranges, units, and human-friendly quantities that
    don't fit a single float. Per-ingredient macros are optional — only present
    when the source table has dedicated macro columns.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    quantity: str | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None


class MealOption(BaseModel):
    """A single meal alternative (e.g. `### Opzione A` OR a grid-cell).

    Plan 02-04 — `day_of_week` is the list of day-of-week ints (0=Mon..6=Sun)
    this option applies to when extracted from a weekly grid. `None` for
    subheading-format (week-level) options.
    """

    model_config = ConfigDict(extra="forbid")

    key: str
    title: str
    ingredients: list[Ingredient] = Field(default_factory=list)
    macros: Macros = Field(default_factory=Macros)
    notes: str | None = None
    # Plan 01-09 — optional photo URL for Lifesum-style meal cards.
    # Phase 1: parser leaves None unless the .md contains a literal `**Foto:** <url>`
    # line in the meal section (extraction is opt-in; existing fixtures parse green).
    # Phase 2 plan editor + upload flow will populate this after URL sanitization.
    # `str | None` rather than HttpUrl so internal URLs / future blob refs stay valid;
    # length capped at 500 chars (Plan 01-09 STRIDE — spoofing mitigation).
    photo_url: str | None = Field(default=None, max_length=500)
    # Plan 02-04 — list of day_of_week ints this option applies to (0=Mon..6=Sun);
    # `None` for week-level / subheading-format options.
    day_of_week: list[int] | None = None
    # Plan 02-05 — optional `**Categoria:** <name>` annotation that overrides
    # the keyword-based mapping in shopping_service.aggregate_for_week. Bounded
    # by parser regex to ≤50 chars; shopping_service additionally validates
    # against the 5 locked categories before applying (T-02-05-01 mitigation).
    category: str | None = Field(default=None, max_length=50)


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
