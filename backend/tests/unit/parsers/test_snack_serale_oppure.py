"""Plan 02-05 — SPUNTINO SERALE plain-bullet + `oppure` connector parser.

Real Stefano plan SERALE section:

  ## SPUNTINO SERALE (opzionale - solo se fame vera)

  - 200 g yogurt di soia non zuccherato
  - oppure 1 scatoletta tonno con cetrioli
  - oppure 20 g cioccolato fondente 85%+

Bug (Plan 02-05 gap-closure): the parser previously only recognized
`- Opzione X: <text>` bullets as alternatives. SERALE uses plain bullets
joined by `oppure` so no alternatives matched → fell through to the legacy
single-segment path → emitted ONE MealOption with `ingredients=[]`.

This file locks the new contract:
  * ≥2 plain `- <text>` bullets (with optional `oppure`/`o ` connectors on
    bullets 2..N) → emit ONE MealOption per bullet.
  * The connector word is stripped from the ingredient name.
  * Each option's ingredients are split on `+` (matches grid-cell convention).
  * Backward compat: plain-prose bodies (no bullets) OR a single bullet stay
    as a single MealOption.
"""

from __future__ import annotations

import pytest

from app.parsers.plan_sections import parse_section

pytestmark = pytest.mark.unit


_STEFANO_SERALE_BODY = """\
- 200 g yogurt di soia non zuccherato
- oppure 1 scatoletta tonno con cetrioli
- oppure 20 g cioccolato fondente 85%+
"""

_PROSE_BODY = """\
Frutta + 30g mandorle
"""


def test_stefano_serale_emits_three_alternatives() -> None:
    """3 plain bullets with `oppure` connectors → 3 MealOption entries."""
    parsed_value, _warnings = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE (opzionale - solo se fame vera)",
    )
    assert isinstance(parsed_value, list)
    assert len(parsed_value) == 3, f"Expected 3 alternatives, got {len(parsed_value)}"


def test_stefano_serale_alternatives_have_ingredients_populated() -> None:
    """Each alternative MUST have non-empty ingredients (this was the bug)."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE (opzionale - solo se fame vera)",
    )
    assert isinstance(parsed_value, list)
    for idx, opt in enumerate(parsed_value):
        ings = opt.get("ingredients") or []
        assert len(ings) >= 1, (
            f"Alternative {idx} ingredients={ings!r} (was bug — empty list rendered)"
        )


def test_stefano_serale_strips_oppure_connector() -> None:
    """`oppure` (and `o `) connector words must NOT survive into ingredient name."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE",
    )
    assert isinstance(parsed_value, list)
    for opt in parsed_value:
        for ing in opt.get("ingredients") or []:
            name_low = ing["name"].lower()
            assert not name_low.startswith("oppure "), (
                f"`oppure` should be stripped, got {ing['name']!r}"
            )
            # The connector must not appear at the very front
            assert not name_low.startswith("o "), f"Stray `o ` connector in {ing['name']!r}"


def test_stefano_serale_alternatives_titles_are_distinct() -> None:
    """Each alternative carries a distinct title for MealCard rendering."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE",
    )
    titles = [opt["title"] for opt in parsed_value]
    assert len(titles) == len(set(titles)), f"Titles must be unique, got {titles}"
    for t in titles:
        assert "Spuntino serale" in t


def test_stefano_serale_alternatives_keys_are_distinct() -> None:
    """Each alternative carries a distinct `key` for variant_by_meal lookup."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE",
    )
    keys = [opt["key"] for opt in parsed_value]
    assert len(keys) == len(set(keys)), f"Keys must be unique, got {keys}"


def test_serale_options_carry_evening_slot() -> None:
    """SERALE heading triggers `slot='evening'` so today_service orders these
    AFTER dinner."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE (opzionale - solo se fame vera)",
    )
    for opt in parsed_value:
        assert opt.get("slot") == "evening"


def test_prose_snack_body_still_emits_single_option() -> None:
    """Backward compat: plain prose body (no bullets) → single MealOption."""
    parsed_value, _ = parse_section(
        "snacks",
        _PROSE_BODY,
        "SPUNTINO POMERIGGIO",
    )
    assert isinstance(parsed_value, list)
    assert len(parsed_value) == 1


def test_first_ingredient_is_first_bullet_text() -> None:
    """Specific spec from the bug report: first option ingredient name should be
    `200 g yogurt di soia non zuccherato`."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE",
    )
    first_ing_names = [i["name"] for i in parsed_value[0]["ingredients"]]
    assert first_ing_names == ["200 g yogurt di soia non zuccherato"]


def test_second_alternative_oppure_stripped_correctly() -> None:
    """Second bullet `- oppure 1 scatoletta...` → `1 scatoletta tonno con cetrioli`."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_SERALE_BODY,
        "SPUNTINO SERALE",
    )
    second_ing_names = [i["name"] for i in parsed_value[1]["ingredients"]]
    assert second_ing_names == ["1 scatoletta tonno con cetrioli"]
