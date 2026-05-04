"""Test grid-format parsing for weekly meal plans (Plan 02-04).

The real Stefano + Marta plans use weekly grid `| Giorno | Opzione A | Opzione B |`
for lunches and dinners. This file locks dual-mode parsing:
  * grid format → dict keyed by day_slug ('lun'..'dom') → list of MealOption dicts
  * subheading format (`### Opzione X`) → dict keyed by 'default' (backward compat)

Day-label tolerance covers Italian variants: Lun / Lunedi / Lunedì / Lun-Gio / Lun, Gio.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.parsers.plan_parser import parse_and_validate
from app.parsers.plan_sections import (
    _parse_day_label,
    _parse_meal_grid,
    parse_section,
)

pytestmark = pytest.mark.unit


def test_parse_simple_grid_two_options() -> None:
    md = """| Giorno | Opzione A | Opzione B |
|--------|-----------|-----------|
| Lun | Pasta al pomodoro | Riso integrale |
| Mar | Pollo grigliato | Insalata mista |
"""
    result = _parse_meal_grid(md)
    assert "lun" in result
    assert "mar" in result
    assert len(result["lun"]) == 2
    titles = [opt["title"] for opt in result["lun"]]
    assert "Pasta al pomodoro" in titles
    assert "Riso integrale" in titles
    # day_of_week list captured on each option
    assert result["lun"][0]["day_of_week"] == [0]
    assert result["mar"][0]["day_of_week"] == [1]


def test_parse_grid_combined_day_label_lun_gio() -> None:
    """`Lun / Gio` row → emit option for both 'lun' and 'gio' day slugs."""
    md = """| Giorno | Opzione A |
|--------|-----------|
| Lun / Gio | Salmone al forno |
"""
    result = _parse_meal_grid(md)
    assert "lun" in result and "gio" in result
    assert result["lun"][0]["title"] == "Salmone al forno"
    assert result["gio"][0]["title"] == "Salmone al forno"
    # day_of_week should record the combined list for both entries
    assert result["lun"][0]["day_of_week"] == [0, 3]
    assert result["gio"][0]["day_of_week"] == [0, 3]


def test_parse_day_label_variants() -> None:
    """Italian day-label tolerance covers short/full/accented/separator variants."""
    assert _parse_day_label("Lun") == [0]
    assert _parse_day_label("Lunedi") == [0]
    assert _parse_day_label("Lunedì") == [0]
    assert _parse_day_label("LUNEDÌ") == [0]
    assert _parse_day_label("Lun / Gio") == [0, 3]
    assert _parse_day_label("Lun-Gio") == [0, 3]
    assert _parse_day_label("Lun, Gio") == [0, 3]
    assert _parse_day_label("Lun & Gio") == [0, 3]
    assert _parse_day_label("Lun&Gio") == [0, 3]
    # All 7 days in canonical short form
    assert _parse_day_label("Dom") == [6]
    assert _parse_day_label("Sab") == [5]
    assert _parse_day_label("Ven") == [4]
    assert _parse_day_label("Mer") == [2]


def test_parse_day_label_unknown_returns_empty() -> None:
    """Unrecognized labels (e.g. 'TOTALE', 'Note') return empty list."""
    assert _parse_day_label("TOTALE") == []
    assert _parse_day_label("xyz") == []
    assert _parse_day_label("") == []


def test_grid_option_default_macros_when_unparseable() -> None:
    """Cell-level macro extraction is best-effort — empty dict / zero macros are valid."""
    md = """| Giorno | Opzione A |
|--------|-----------|
| Lun | Insalata mista |
"""
    result = _parse_meal_grid(md)
    opt = result["lun"][0]
    # ingredients always [] for grid cells; macros either {} or all-zero
    assert opt["ingredients"] == []
    macros = opt.get("macros", {})
    # Either empty (which Pydantic will fill in via Macros default factory) or zeroed
    if macros:
        assert macros.get("kcal", 0) == 0
        assert macros.get("protein_g", 0) == 0
        assert macros.get("carbs_g", 0) == 0
        assert macros.get("fat_g", 0) == 0


def test_subheading_format_backward_compat() -> None:
    """`### Opzione A` subheading format from EXAMPLE.md still produces 'default' key."""
    md = """### Opzione A — Pasta al pesto

Pasta integrale 80g, pesto 1 cucchiaio.

### Opzione B — Riso

Riso 70g, verdure miste.
"""
    parsed_value, _warnings = parse_section("lunches", md, "PRANZI")
    assert isinstance(parsed_value, dict)
    assert "default" in parsed_value
    assert len(parsed_value["default"]) == 2
    titles = [opt["title"] for opt in parsed_value["default"]]
    # Title cleaning may transform "Opzione a" / "Opzione b" — accept either form.
    assert any("Opzione" in t for t in titles)


def test_grid_emits_one_default_option_when_only_one_column() -> None:
    """Single-option grids still produce a list per day."""
    md = """| Giorno | Piatto |
|--------|--------|
| Mer | Petto di pollo |
| Ven | Salmone |
"""
    result = _parse_meal_grid(md)
    assert "mer" in result and "ven" in result
    assert len(result["mer"]) == 1
    assert result["mer"][0]["title"] == "Petto di pollo"
    assert result["ven"][0]["title"] == "Salmone"


def test_grid_skips_total_rows_and_unknown_day_labels() -> None:
    """A row whose first cell does not parse as days is skipped (not crashed)."""
    md = """| Giorno | Opzione A |
|--------|-----------|
| Lun | Pasta |
| TOTALE | placeholder |
"""
    result = _parse_meal_grid(md)
    assert "lun" in result
    assert len(result["lun"]) == 1
    # TOTALE row must NOT create a key
    assert "totale" not in result


def test_real_plan_stefano_lunches_non_empty() -> None:
    """Real Stefano plan parses: lunches dict has ≥5 day keys (lun..dom or merged)."""
    plan_path = Path(__file__).resolve().parents[4] / "plans" / "PIANO_NUTRIZIONALE_STEFANO.md"
    if not plan_path.exists():
        pytest.skip("Stefano plan fixture not present in this checkout")
    data = plan_path.read_bytes()
    parsed, _report = parse_and_validate(data)
    lunches = parsed.lunches
    assert isinstance(lunches, dict)
    day_keys = set(lunches.keys()) - {"default"}
    assert len(day_keys) >= 5, f"Expected ≥5 day keys, got {sorted(day_keys)}"
    # At least one lunch entry should have a non-empty title (the actual recipe text)
    sample = next(iter(lunches.values()))
    assert isinstance(sample, list)
    assert len(sample) >= 1
    assert sample[0].title


def test_real_plan_stefano_dinners_non_empty() -> None:
    """Real Stefano plan dinners section also parses to per-day dict."""
    plan_path = Path(__file__).resolve().parents[4] / "plans" / "PIANO_NUTRIZIONALE_STEFANO.md"
    if not plan_path.exists():
        pytest.skip("Stefano plan fixture not present in this checkout")
    data = plan_path.read_bytes()
    parsed, _report = parse_and_validate(data)
    dinners = parsed.dinners
    assert isinstance(dinners, dict)
    day_keys = set(dinners.keys()) - {"default"}
    assert len(day_keys) >= 5, f"Expected ≥5 day keys for dinners, got {sorted(day_keys)}"


def test_real_plan_marta_lunches_non_empty() -> None:
    """Real Marta plan also parses to per-day dict."""
    plan_path = Path(__file__).resolve().parents[4] / "plans" / "PIANO_NUTRIZIONALE_MARTA.md"
    if not plan_path.exists():
        pytest.skip("Marta plan fixture not present in this checkout")
    data = plan_path.read_bytes()
    parsed, _report = parse_and_validate(data)
    # Either grid (per-day) or fallback (default) must be present
    assert isinstance(parsed.lunches, dict)
    assert len(parsed.lunches) >= 1
