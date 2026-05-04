"""Shopping service unit tests (SHOP-01..SHOP-04, Pitfall #14).

Plan 02-05 Task 2 — RED phase.

Covers the pure functions that have no DB dependency:
  * ``_format_quantity_it`` — italian rendering ("400 g", "q.b.", "1,5 kg").
  * Aggregation invariants: same (canonical_name, unit) merges; distinct units
    split; ``q.b.`` rows count = 1 regardless of recipe count.
"""

from __future__ import annotations

import pytest

from app.services.shopping_service import _aggregate_ingredients, _format_quantity_it


@pytest.mark.parametrize(
    "amount,unit,expected",
    [
        (200.0, "g", "200 g"),
        (1.5, "kg", "1,5 kg"),
        (2.0, "confezione", "2 confezione"),
        (None, "qb", "q.b."),
        (300.0, "ml", "300 ml"),
        (None, None, ""),
        (0.5, "l", "0,5 l"),
        (10.0, None, "10"),
    ],
)
def test_format_quantity_it(amount: float | None, unit: str | None, expected: str) -> None:
    assert _format_quantity_it(amount, unit) == expected


def test_aggregation_merges_same_name_unit() -> None:
    """Two meals each with ``pomodoro 100g`` collapse into a single 200 g row."""
    meals = [
        {
            "ingredients": ["pomodoro 100g"],
            "category": None,
            "source_label": "lunch_d0",
        },
        {
            "ingredients": ["pomodoro 100g"],
            "category": None,
            "source_label": "dinner_d2",
        },
    ]
    result = _aggregate_ingredients(meals)
    pomodoros = [r for r in result if r["canonical_name"] == "pomodoro"]
    assert len(pomodoros) == 1
    assert pomodoros[0]["amount"] == 200.0
    assert pomodoros[0]["unit"] == "g"
    assert "lunch_d0" in pomodoros[0]["sources"]
    assert "dinner_d2" in pomodoros[0]["sources"]


def test_aggregation_splits_distinct_units() -> None:
    """Same name, different unit (`g` vs `confezione`) → 2 rows."""
    meals = [
        {"ingredients": ["pasta 80g"], "category": None, "source_label": "lunch_d0"},
        {
            "ingredients": ["1 confezione di pasta"],
            "category": None,
            "source_label": "lunch_d1",
        },
    ]
    result = _aggregate_ingredients(meals)
    pastas = [r for r in result if "pasta" in r["canonical_name"]]
    units = sorted({r["unit"] for r in pastas})
    assert "g" in units
    assert "confezione" in units


def test_aggregation_qb_count_is_one() -> None:
    """``q.b.`` rows count = 1 regardless of how many recipes use the ingredient."""
    meals = [
        {"ingredients": ["sale q.b."], "category": None, "source_label": "lunch_d0"},
        {"ingredients": ["sale q.b."], "category": None, "source_label": "dinner_d0"},
        {"ingredients": ["sale q.b."], "category": None, "source_label": "dinner_d4"},
    ]
    result = _aggregate_ingredients(meals)
    salts = [r for r in result if r["canonical_name"] == "sale"]
    assert len(salts) == 1
    assert salts[0]["unit"] == "qb"
    assert salts[0]["amount"] is None
    # Sources still record all 3 contributions for "Per giorno" view
    assert len(salts[0]["sources"]) == 3


def test_aggregation_explicit_category_overrides_keyword() -> None:
    """Meal-level ``**Categoria:**`` annotation wins over keyword lookup."""
    meals = [
        {
            "ingredients": ["pomodoro 100g"],
            "category": "Frigo & Freschi",  # explicit override
            "source_label": "lunch_d0",
        }
    ]
    result = _aggregate_ingredients(meals)
    assert result[0]["category"] == "Frigo & Freschi"


def test_aggregation_invalid_explicit_category_falls_back_to_dispensa() -> None:
    """T-02-05-01 — unknown category string is rejected; fallback applies."""
    meals = [
        {
            "ingredients": ["xyz unknown thing"],
            "category": "Some Made Up Category",
            "source_label": "lunch_d0",
        }
    ]
    result = _aggregate_ingredients(meals)
    # invalid annotation → fallback; xyz is not in keyword map → Dispensa
    assert result[0]["category"] == "Dispensa"
