"""Unit tests for today_service per-day variant resolution (Plan 02-04).

Locks the contract that `_meals_from_parsed` picks lunch/dinner from the day-slug
keyed dict (`lunches: {lun: [...], mar: [...], ...}`) when the user is on that day,
falling back to `'default'` for subheading-format plans, and returning empty when
neither shape is available.
"""

from __future__ import annotations

import pytest

from app.services.today_service import _meals_from_parsed, _options_for_day

pytestmark = pytest.mark.unit


_GRID_PARSED = {
    "lunches": {
        "lun": [
            {
                "key": "opzione_a",
                "title": "Pasta al pomodoro",
                "ingredients": [],
                "macros": {"kcal": 480, "protein_g": 25, "carbs_g": 70, "fat_g": 10},
            },
            {
                "key": "opzione_b",
                "title": "Riso integrale + bresaola",
                "ingredients": [],
                "macros": {"kcal": 460, "protein_g": 38, "carbs_g": 60, "fat_g": 9},
            },
        ],
        "mer": [
            {
                "key": "opzione_a",
                "title": "Petto di pollo + pane integrale",
                "ingredients": [],
                "macros": {"kcal": 470, "protein_g": 42, "carbs_g": 55, "fat_g": 8},
            }
        ],
    },
    "dinners": {
        "lun": [
            {
                "key": "opzione_a",
                "title": "Salmone al forno",
                "ingredients": [],
                "macros": {"kcal": 700, "protein_g": 50, "carbs_g": 40, "fat_g": 35},
            }
        ]
    },
    "snacks": [],
}

_SUBHEADING_PARSED = {
    "lunches": {
        "default": [
            {
                "key": "A",
                "title": "Pasta integrale",
                "ingredients": [],
                "macros": {"kcal": 720, "protein_g": 28, "carbs_g": 90, "fat_g": 18},
            },
            {
                "key": "B",
                "title": "Riso e verdure",
                "ingredients": [],
                "macros": {"kcal": 680, "protein_g": 22, "carbs_g": 95, "fat_g": 14},
            },
        ]
    },
    "dinners": {
        "default": [
            {
                "key": "A",
                "title": "Salmone alla griglia",
                "ingredients": [],
                "macros": {"kcal": 620, "protein_g": 45, "carbs_g": 30, "fat_g": 28},
            }
        ]
    },
    "snacks": [],
}


def test_options_for_day_grid_returns_today_lunches() -> None:
    """Mon (dow=0) → lunches['lun']."""
    options = _options_for_day(_GRID_PARSED["lunches"], 0)
    assert len(options) == 2
    assert options[0]["title"] == "Pasta al pomodoro"


def test_options_for_day_grid_returns_wednesday_lunches() -> None:
    """Wed (dow=2) → lunches['mer']."""
    options = _options_for_day(_GRID_PARSED["lunches"], 2)
    assert len(options) == 1
    assert options[0]["title"] == "Petto di pollo + pane integrale"


def test_options_for_day_grid_falls_back_to_default_when_day_missing() -> None:
    """Tue (dow=1) — not in grid above. Falls back to first non-empty list value."""
    options = _options_for_day(_GRID_PARSED["lunches"], 1)
    # No 'mar' key, no 'default' key → defensive: return any first non-empty list.
    assert len(options) >= 1


def test_options_for_day_subheading_default_used_for_any_day() -> None:
    """Subheading-format plan: 'default' key serves every day."""
    options_mon = _options_for_day(_SUBHEADING_PARSED["lunches"], 0)
    options_fri = _options_for_day(_SUBHEADING_PARSED["lunches"], 4)
    assert options_mon == options_fri
    assert options_mon[0]["title"] == "Pasta integrale"


def test_options_for_day_empty_dict_returns_empty_list() -> None:
    """No options at all → empty list, no crash."""
    assert _options_for_day({}, 0) == []
    assert _options_for_day(None, 0) == []  # type: ignore[arg-type]


def test_meals_from_parsed_grid_monday_picks_lun_lunch() -> None:
    """Plan 02-04: Monday user sees 'Pasta al pomodoro' (first opt of lun)."""
    meals = _meals_from_parsed(_GRID_PARSED, day_of_week=0)
    lunch = next((m for m in meals if m.meal_type == "lunch"), None)
    assert lunch is not None
    assert lunch.title == "Pasta al pomodoro"


def test_meals_from_parsed_grid_wednesday_picks_mer_lunch() -> None:
    """Plan 02-04: Wednesday user sees the Wed-specific lunch ('Petto di pollo')."""
    meals = _meals_from_parsed(_GRID_PARSED, day_of_week=2)
    lunch = next((m for m in meals if m.meal_type == "lunch"), None)
    assert lunch is not None
    assert lunch.title == "Petto di pollo + pane integrale"


def test_meals_from_parsed_subheading_default_works_any_day() -> None:
    """Subheading-format plan: every day picks 'default' first option."""
    meals_mon = _meals_from_parsed(_SUBHEADING_PARSED, day_of_week=0)
    meals_fri = _meals_from_parsed(_SUBHEADING_PARSED, day_of_week=4)
    lunch_mon = next(m for m in meals_mon if m.meal_type == "lunch")
    lunch_fri = next(m for m in meals_fri if m.meal_type == "lunch")
    assert lunch_mon.title == lunch_fri.title == "Pasta integrale"


def test_meals_from_parsed_no_lunches_dict_no_crash() -> None:
    """Defensive: parsed_json missing lunches/dinners returns no lunch/dinner entries."""
    meals = _meals_from_parsed({"breakfast": {"key": "default", "title": "Yogurt"}}, day_of_week=0)
    # Breakfast survives, lunch/dinner skipped silently.
    assert all(m.meal_type != "lunch" for m in meals)
    assert all(m.meal_type != "dinner" for m in meals)


def test_meals_from_parsed_variant_by_meal_overrides_first_option() -> None:
    """When a stored variant exists, surface that variant's title (not first option)."""

    class FakeVariant:
        def __init__(self, key: str) -> None:
            self.variant_key = key

    meals = _meals_from_parsed(
        _GRID_PARSED,
        day_of_week=0,
        variant_by_meal={"lunch": FakeVariant("opzione_b")},  # type: ignore[dict-item]
    )
    lunch = next(m for m in meals if m.meal_type == "lunch")
    # variant_by_meal switched lunch from opzione_a to opzione_b
    assert lunch.title == "Riso integrale + bresaola"
    assert lunch.variant_key == "opzione_b"


def test_meals_from_parsed_unknown_variant_key_falls_back_to_first() -> None:
    """Stored variant key not in current options → fallback to first option."""

    class FakeVariant:
        def __init__(self, key: str) -> None:
            self.variant_key = key

    meals = _meals_from_parsed(
        _GRID_PARSED,
        day_of_week=0,
        variant_by_meal={"lunch": FakeVariant("opzione_zzz_unknown")},  # type: ignore[dict-item]
    )
    lunch = next(m for m in meals if m.meal_type == "lunch")
    # Falls back to first option.
    assert lunch.title == "Pasta al pomodoro"
