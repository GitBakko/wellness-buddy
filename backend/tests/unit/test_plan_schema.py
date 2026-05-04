"""Unit tests for app/schemas/plan_parsed.py — strict Pydantic v2 schema (extra='forbid').

Source: PLAN-06, T-PARSE-03 (crafted JSON bypass downstream consumers).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.plan_parsed import (
    Macros,
    MealOption,
    PersonalData,
    PlanParsedSchema,
)

pytestmark = pytest.mark.unit


def test_minimal_valid() -> None:
    s = PlanParsedSchema.model_validate({})
    assert s.macro_target.kcal == 0
    assert s.lunches == {}
    assert s.dinners == {}
    assert s.snacks == []
    assert s.rules == []
    assert s.personal_data is None


def test_strict_rejects_extra_field_root() -> None:
    with pytest.raises(ValidationError):
        PlanParsedSchema.model_validate({"foo": "bar"})


def test_strict_rejects_extra_field_nested() -> None:
    with pytest.raises(ValidationError):
        PlanParsedSchema.model_validate({"personal_data": {"name": "X", "junk_field": 1}})


def test_macros_strict() -> None:
    Macros.model_validate({"kcal": 100, "protein_g": 1, "carbs_g": 2, "fat_g": 3})
    with pytest.raises(ValidationError):
        Macros.model_validate({"kcal": 100, "extra": True})


def test_meal_option_strict() -> None:
    MealOption.model_validate({"key": "A", "title": "T"})
    with pytest.raises(ValidationError):
        MealOption.model_validate({"key": "A", "title": "T", "junk": 1})


def test_personal_data_optional_fields() -> None:
    pd = PersonalData.model_validate({"name": "Mario"})
    assert pd.name == "Mario"
    assert pd.age is None
    assert pd.current_weight_kg is None


def test_plan_parsed_with_full_payload() -> None:
    payload = {
        "personal_data": {"name": "Stefano", "age": 42, "current_weight_kg": 84.0},
        "macro_target": {"kcal": 2200, "protein_g": 165, "carbs_g": 220, "fat_g": 75},
        "daily_structure": [{"raw": "Colazione 07:30"}],
        "breakfast": {"key": "default", "title": "Yogurt"},
        "lunches": {"default": [{"key": "A", "title": "Pasta"}]},
        "dinners": {"default": [{"key": "A", "title": "Salmone"}]},
        "snacks": [{"key": "default", "title": "Frutta"}],
        "supplements": [{"raw": "Multivitaminico"}],
        "weight_projection": [{"raw": "Settimana 1"}],
        "rules": ["2L acqua"],
    }
    schema = PlanParsedSchema.model_validate(payload)
    assert schema.personal_data is not None and schema.personal_data.name == "Stefano"
    assert schema.macro_target.kcal == 2200
    assert schema.lunches["default"][0].title == "Pasta"
    assert schema.rules == ["2L acqua"]
