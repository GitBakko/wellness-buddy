"""Test snack `- Opzione X:` bullets parse as ALTERNATIVE MealOptions, not as
combined ingredients of a single option.

Bug (Plan 02-05 gap-closure): real Stefano + Marta plans use
`## SPUNTINO POMERIGGIO` followed by `- Opzione A: ...`, `- Opzione B: ...` etc.
The user must CHOOSE ONE alternative — not eat all 4. Previously the parser
collapsed all bullets into ingredients of a single MealOption, causing MealCard
to render the 4 alternatives as a single must-eat-all list.

This file locks the new contract:
  * `Opzione X:` bullets (≥2) → emit MULTIPLE MealOption (one per bullet)
  * Each MealOption title = "<Section title cleaned> - Opzione X"
  * Each MealOption ingredients = bullet text split on `+`
  * Backward compat: snack body WITHOUT `Opzione X:` bullets → single MealOption
    with bullets as ingredients (or empty when no bullets at all).
"""

from __future__ import annotations

import pytest

from app.parsers.plan_sections import parse_section

pytestmark = pytest.mark.unit


_STEFANO_POMERIGGIO_BODY = """\
Gli elettroliti durante il workout di 30 minuti sono fisiologicamente inutili.
Il pomeriggio e il momento ottimale: combatte il calo energetico post-pranzo.

- Opzione A: 200 g yogurt di soia/cocco non zuccherato + 10 g noci
- Opzione B: 30 g mandorle o noci miste
- Opzione C: 1 frutto medio (mela/pera) + 20 g noci
- Opzione D: 2 barrette homemade + 150 g yogurt di soia non zuccherato
"""

_MARTA_POMERIGGIO_BODY = """\
- Opzione A: 150 g yogurt greco intero + 5 mandorle  (~180 kcal / ~14 g proteine)
- Opzione B: 1 frutto medio + 20 g noci  (~160 kcal / ~4 g proteine)
- Opzione C: 1-2 barrette homemade di Stefano  (~83-165 kcal)
- Opzione D: 30 g parmigiano o grana + 1 frutto  (~170 kcal / ~10 g proteine)
"""

_SIMPLE_BODY_NO_OPZIONE = """\
Frutta + 30g mandorle
"""

_SERALE_BODY = """\
- 200 g yogurt di soia non zuccherato
- oppure 1 scatoletta tonno con cetrioli
- oppure 20 g cioccolato fondente 85%+
"""


def test_stefano_pomeriggio_emits_four_alternatives() -> None:
    """4 `- Opzione X:` bullets → 4 separate MealOption entries."""
    parsed_value, _warnings = parse_section(
        "snacks",
        _STEFANO_POMERIGGIO_BODY,
        "SPUNTINO POMERIGGIO (15:30-16:00) + Elettroliti",
    )
    assert isinstance(parsed_value, list)
    assert len(parsed_value) == 4
    titles = [opt["title"] for opt in parsed_value]
    # Each title surfaces the alternative letter so the user can SEE it's a choice.
    assert "Opzione A" in titles[0]
    assert "Opzione B" in titles[1]
    assert "Opzione C" in titles[2]
    assert "Opzione D" in titles[3]
    # And the section name is still present (so MealCard can show context).
    for t in titles:
        assert "Spuntino pomeriggio" in t.lower() or "spuntino" in t.lower()


def test_stefano_pomeriggio_keys_are_distinct_per_option() -> None:
    """Each option must have a unique key for variant_by_meal lookup."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_POMERIGGIO_BODY,
        "SPUNTINO POMERIGGIO (15:30-16:00) + Elettroliti",
    )
    assert isinstance(parsed_value, list)
    keys = [opt["key"] for opt in parsed_value]
    assert len(keys) == len(set(keys)), f"Keys must be unique, got {keys}"
    # Convention: <base_slug>__opzione_<x>
    assert all("__opzione_" in k for k in keys), f"Expected `__opzione_<x>` keys, got {keys}"


def test_stefano_pomeriggio_ingredients_split_on_plus() -> None:
    """Bullet text is split on `+` so MealCard can render composition.

    `Opzione A: 200 g yogurt di soia/cocco non zuccherato + 10 g noci` →
    [{name: '200 g yogurt di soia/cocco non zuccherato'}, {name: '10 g noci'}]
    """
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_POMERIGGIO_BODY,
        "SPUNTINO POMERIGGIO (15:30-16:00) + Elettroliti",
    )
    assert isinstance(parsed_value, list)
    opt_a = parsed_value[0]
    names_a = [ing["name"] for ing in opt_a["ingredients"]]
    assert "200 g yogurt di soia/cocco non zuccherato" in names_a
    assert "10 g noci" in names_a

    opt_b = parsed_value[1]
    # Single-ingredient opzione → one ingredient row
    names_b = [ing["name"] for ing in opt_b["ingredients"]]
    assert names_b == ["30 g mandorle o noci miste"]


def test_marta_pomeriggio_drops_trailing_macro_hint() -> None:
    """Trailing `(~XXX kcal / ~XX g proteine)` hint is stripped from ingredient name."""
    parsed_value, _ = parse_section(
        "snacks",
        _MARTA_POMERIGGIO_BODY,
        "SPUNTINO POMERIGGIO (15:30-16:00) (~150 kcal)",
    )
    assert isinstance(parsed_value, list)
    assert len(parsed_value) == 4
    opt_a = parsed_value[0]
    names_a = [ing["name"] for ing in opt_a["ingredients"]]
    # No "~180 kcal" leftover anywhere
    for n in names_a:
        assert "kcal" not in n.lower()
        assert "proteine" not in n.lower()
    # The actual ingredients survived
    assert any("yogurt greco" in n for n in names_a)
    assert any("mandorle" in n for n in names_a)


def test_simple_snack_no_opzione_pattern_yields_single_option() -> None:
    """Backward compat: snack body WITHOUT `Opzione X:` → single MealOption."""
    parsed_value, _ = parse_section(
        "snacks",
        _SIMPLE_BODY_NO_OPZIONE,
        "SPUNTINO POMERIGGIO",
    )
    assert isinstance(parsed_value, list)
    assert len(parsed_value) == 1
    assert parsed_value[0]["title"] == "Spuntino pomeriggio"


def test_serale_oppure_bullets_yield_single_option() -> None:
    """SPUNTINO SERALE uses `- 200 g yogurt`/`- oppure ...` plain bullets — NOT
    `Opzione X:` pattern. Should still emit a single option (backward compat)."""
    parsed_value, _ = parse_section(
        "snacks",
        _SERALE_BODY,
        "SPUNTINO SERALE (opzionale - solo se fame vera)",
    )
    assert isinstance(parsed_value, list)
    assert len(parsed_value) == 1
    assert "Spuntino serale" in parsed_value[0]["title"]


def test_macros_zeroed_for_alternatives() -> None:
    """Each alternative carries zero macros — proportional allocation lives in
    today_service / weekly_service so the snack-pool split is honored."""
    parsed_value, _ = parse_section(
        "snacks",
        _STEFANO_POMERIGGIO_BODY,
        "SPUNTINO POMERIGGIO",
    )
    for opt in parsed_value:
        macros = opt.get("macros", {}) or {}
        if macros:
            assert macros.get("kcal", 0) == 0
            assert macros.get("protein_g", 0) == 0
            assert macros.get("carbs_g", 0) == 0
            assert macros.get("fat_g", 0) == 0


def test_one_opzione_only_still_emits_one_option() -> None:
    """Edge case: section has only ONE `Opzione X:` bullet — still emits one
    titled MealOption. (Real plans always have ≥2, but defensive.)"""
    body = "- Opzione A: 200 g yogurt + 30 g mandorle\n"
    parsed_value, _ = parse_section("snacks", body, "SPUNTINO POMERIGGIO")
    assert isinstance(parsed_value, list)
    assert len(parsed_value) == 1
    # Single Opzione still shows the alternative letter so labelling is consistent.
    assert "Opzione A" in parsed_value[0]["title"]
    names = [ing["name"] for ing in parsed_value[0]["ingredients"]]
    assert names == ["200 g yogurt", "30 g mandorle"]
