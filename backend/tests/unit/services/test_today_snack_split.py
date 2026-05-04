"""Test today_service snack-pool split groups by base section so each option
carries its section share (not a fraction of total options).

Bug (Plan 02-05 gap-closure): when the parser emits N alternative MealOptions
per snack section (e.g. SPUNTINO POMERIGGIO has 4 Opzione A..D), the previous
split logic divided 10% across all N entries → each option got 10/N% of daily
kcal, which is WRONG (the user only eats ONE alternative per section).

Correct logic: group snacks by base section key (extract from `key` by
splitting on `__opzione`). 2 sections → each section gets 5% of daily kcal.
Within a section, every option carries the FULL section share (since user
picks one). User eats Opzione A + Serale → 5% + 5% = 10% total.
"""

from __future__ import annotations

import pytest

from app.services.today_service import _meals_from_parsed

pytestmark = pytest.mark.unit


_DAILY_TARGET = {"kcal": 2000, "protein_g": 160, "carbs_g": 200, "fat_g": 60}


def _stefano_parsed_two_sections_four_plus_one() -> dict:
    """Parser-shaped dict mirroring real Stefano: 2 sections × {4 + 1} options.

    SPUNTINO POMERIGGIO has 4 Opzione A..D alternatives.
    SPUNTINO SERALE has 1 option.
    """
    return {
        "macro_target": dict(_DAILY_TARGET),
        "breakfast": None,
        "lunches": {},
        "dinners": {},
        "snacks": [
            {
                "key": "spuntino_pomeriggio__opzione_a",
                "title": "Spuntino pomeriggio - Opzione A",
                "ingredients": [{"name": "yogurt"}, {"name": "noci"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            },
            {
                "key": "spuntino_pomeriggio__opzione_b",
                "title": "Spuntino pomeriggio - Opzione B",
                "ingredients": [{"name": "mandorle"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            },
            {
                "key": "spuntino_pomeriggio__opzione_c",
                "title": "Spuntino pomeriggio - Opzione C",
                "ingredients": [{"name": "frutto"}, {"name": "noci"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            },
            {
                "key": "spuntino_pomeriggio__opzione_d",
                "title": "Spuntino pomeriggio - Opzione D",
                "ingredients": [{"name": "barrette"}, {"name": "yogurt"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            },
            {
                "key": "spuntino_serale",
                "title": "Spuntino serale",
                "ingredients": [{"name": "yogurt"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            },
        ],
    }


def test_split_groups_by_base_section_two_sections_each_5_percent() -> None:
    """2 base sections → each section gets 5% of daily kcal (snack pool 10% / 2).

    Every option within a section carries that 5% — since the user eats ONE
    alternative per section, total intake per section = section share.
    """
    parsed = _stefano_parsed_two_sections_four_plus_one()
    meals = _meals_from_parsed(parsed, day_of_week=0)
    snacks = [m for m in meals if m.meal_type == "snack"]
    assert len(snacks) == 5  # 4 pomeriggio + 1 serale

    # Daily 2000 × 10% = 200 kcal total snack pool.
    # 2 sections → 100 kcal per section, every option in each section.
    for s in snacks:
        assert s.macros.kcal == 100, f"{s.title} kcal={s.macros.kcal}, expected 100"


def test_single_section_keeps_full_snack_share() -> None:
    """Single snack section → carries the full 10% share."""
    parsed = {
        "macro_target": dict(_DAILY_TARGET),
        "snacks": [
            {
                "key": "afternoon",
                "title": "Spuntino",
                "ingredients": [{"name": "yogurt"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            }
        ],
    }
    meals = _meals_from_parsed(parsed, day_of_week=0)
    snacks = [m for m in meals if m.meal_type == "snack"]
    assert len(snacks) == 1
    # 2000 × 10% = 200 kcal — single section gets the full pool.
    assert snacks[0].macros.kcal == 200


def test_section_with_multiple_options_each_carries_section_share() -> None:
    """Section with 4 alternative options → each option gets the FULL section
    share (since user eats one)."""
    parsed = {
        "macro_target": dict(_DAILY_TARGET),
        "snacks": [
            {
                "key": "spuntino_pomeriggio__opzione_a",
                "title": "Spuntino pomeriggio - Opzione A",
                "ingredients": [],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            },
            {
                "key": "spuntino_pomeriggio__opzione_b",
                "title": "Spuntino pomeriggio - Opzione B",
                "ingredients": [],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            },
        ],
    }
    meals = _meals_from_parsed(parsed, day_of_week=0)
    snacks = [m for m in meals if m.meal_type == "snack"]
    assert len(snacks) == 2
    # Single section (pomeriggio) → 10% of 2000 = 200 kcal per option (each is
    # an alternative, not a sum).
    for s in snacks:
        assert s.macros.kcal == 200


def test_split_preserves_explicit_macros_when_provided() -> None:
    """If a snack option carries non-zero macros (legacy ingredient-table plans),
    those win — proportional split is only the fallback for zero macros."""
    parsed = {
        "macro_target": dict(_DAILY_TARGET),
        "snacks": [
            {
                "key": "explicit",
                "title": "Spuntino esplicito",
                "ingredients": [],
                "macros": {"kcal": 280, "protein_g": 8, "carbs_g": 32, "fat_g": 14},
            }
        ],
    }
    meals = _meals_from_parsed(parsed, day_of_week=0)
    snacks = [m for m in meals if m.meal_type == "snack"]
    assert len(snacks) == 1
    assert snacks[0].macros.kcal == 280
