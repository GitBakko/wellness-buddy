"""Plan 02-05 — today_service orders evening snacks AFTER dinner.

Bug (Plan 02-05 gap-closure): `_meals_from_parsed` previously placed ALL
snacks (POMERIGGIO + SERALE) between lunch and dinner. Stefano's plan has
SERALE labelled "opzionale - solo se fame vera" and is consumed AFTER
dinner. The render order on /today must split snacks by their slot:

    breakfast → lunch → afternoon snacks → dinner → evening snacks

Implementation: MealOption.slot field carries `"afternoon" | "evening" | None`.
today_service splits the snack list by slot before assembling the ordered
result. `None` defaults to afternoon (backward compat for legacy parsed_json).
"""

from __future__ import annotations

import pytest

from app.services.today_service import _meals_from_parsed

pytestmark = pytest.mark.unit


_DAILY_TARGET = {"kcal": 2000, "protein_g": 160, "carbs_g": 200, "fat_g": 60}


def _build_parsed(*, afternoon_count: int, evening_count: int) -> dict:
    """Synthetic parsed_json with breakfast + lunch + dinner + N afternoon + M evening snacks."""
    snacks: list[dict] = []
    for i in range(afternoon_count):
        snacks.append(
            {
                "key": f"spuntino_pomeriggio__opzione_{chr(ord('a') + i)}",
                "title": f"Spuntino pomeriggio - Opzione {chr(ord('A') + i)}",
                "ingredients": [{"name": "yogurt"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                "slot": "afternoon",
            }
        )
    for i in range(evening_count):
        snacks.append(
            {
                "key": f"spuntino_serale__opzione_{i + 1}",
                "title": f"Spuntino serale - Alternativa {i + 1}",
                "ingredients": [{"name": "yogurt soia"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                "slot": "evening",
            }
        )
    return {
        "macro_target": dict(_DAILY_TARGET),
        "breakfast": {
            "key": "default",
            "title": "Colazione",
            "ingredients": [],
            "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
        },
        "lunches": {
            "default": [
                {
                    "key": "opzione_a",
                    "title": "Pranzo",
                    "ingredients": [],
                    "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                }
            ]
        },
        "dinners": {
            "default": [
                {
                    "key": "opzione_a",
                    "title": "Cena",
                    "ingredients": [],
                    "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                }
            ]
        },
        "snacks": snacks,
    }


def test_one_afternoon_one_evening_orders_breakfast_lunch_afternoon_dinner_evening() -> None:
    """Spec: 1 afternoon snack + dinner + 1 evening snack →
    [breakfast, lunch, afternoon, dinner, evening]."""
    parsed = _build_parsed(afternoon_count=1, evening_count=1)
    meals = _meals_from_parsed(parsed, day_of_week=0)
    types = [m.meal_type for m in meals]
    assert types == ["breakfast", "lunch", "snack", "dinner", "snack"]
    # The first snack title is afternoon, the second is evening
    snacks = [m for m in meals if m.meal_type == "snack"]
    assert "pomeriggio" in snacks[0].title.lower()
    assert "serale" in snacks[1].title.lower()


def test_two_afternoon_options_one_evening_evening_after_dinner() -> None:
    """2 afternoon (Opzione A/B) + dinner + 1 evening:
    all afternoon options come BEFORE dinner, evening AFTER dinner."""
    parsed = _build_parsed(afternoon_count=2, evening_count=1)
    meals = _meals_from_parsed(parsed, day_of_week=0)
    types = [m.meal_type for m in meals]
    # Expected: breakfast, lunch, 2× afternoon snack, dinner, 1× evening snack
    assert types == ["breakfast", "lunch", "snack", "snack", "dinner", "snack"]
    snacks = [m for m in meals if m.meal_type == "snack"]
    # First two snacks are pomeriggio
    assert "pomeriggio" in snacks[0].title.lower()
    assert "pomeriggio" in snacks[1].title.lower()
    # Last snack is serale (after dinner)
    assert "serale" in snacks[2].title.lower()


def test_four_afternoon_three_evening_full_stefano_layout() -> None:
    """Real Stefano: 4 POMERIGGIO Opzione A..D + 3 SERALE alternatives.
    Order: breakfast → lunch → 4 afternoon → dinner → 3 evening."""
    parsed = _build_parsed(afternoon_count=4, evening_count=3)
    meals = _meals_from_parsed(parsed, day_of_week=0)
    types = [m.meal_type for m in meals]
    assert types == [
        "breakfast",
        "lunch",
        "snack",
        "snack",
        "snack",
        "snack",
        "dinner",
        "snack",
        "snack",
        "snack",
    ]
    snacks = [m for m in meals if m.meal_type == "snack"]
    # First 4 are afternoon (pomeriggio), last 3 are evening (serale)
    for i in range(4):
        assert "pomeriggio" in snacks[i].title.lower(), (
            f"Position {i} should be afternoon, got {snacks[i].title}"
        )
    for i in range(4, 7):
        assert "serale" in snacks[i].title.lower(), (
            f"Position {i} should be evening, got {snacks[i].title}"
        )


def test_legacy_snack_without_slot_defaults_to_afternoon() -> None:
    """Backward compat: legacy parsed_json without `slot` field → treated as afternoon
    (renders BEFORE dinner)."""
    parsed = {
        "macro_target": dict(_DAILY_TARGET),
        "breakfast": {"key": "default", "title": "Colazione"},
        "lunches": {"default": [{"key": "a", "title": "Pranzo"}]},
        "dinners": {"default": [{"key": "a", "title": "Cena"}]},
        "snacks": [
            # No `slot` field — legacy data
            {
                "key": "afternoon_legacy",
                "title": "Spuntino",
                "ingredients": [{"name": "yogurt"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            }
        ],
    }
    meals = _meals_from_parsed(parsed, day_of_week=0)
    types = [m.meal_type for m in meals]
    # Snack must appear BEFORE dinner (afternoon default).
    assert types == ["breakfast", "lunch", "snack", "dinner"]


def test_only_evening_snack_no_afternoon_orders_after_dinner() -> None:
    """Edge: only an evening snack (no afternoon) → evening still goes AFTER dinner."""
    parsed = _build_parsed(afternoon_count=0, evening_count=1)
    meals = _meals_from_parsed(parsed, day_of_week=0)
    types = [m.meal_type for m in meals]
    assert types == ["breakfast", "lunch", "dinner", "snack"]


def test_only_afternoon_snacks_no_evening() -> None:
    """Edge: only afternoon snacks (no evening) → all snacks before dinner."""
    parsed = _build_parsed(afternoon_count=2, evening_count=0)
    meals = _meals_from_parsed(parsed, day_of_week=0)
    types = [m.meal_type for m in meals]
    assert types == ["breakfast", "lunch", "snack", "snack", "dinner"]
