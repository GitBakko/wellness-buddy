"""Test `**Categoria:** <name>` annotation extraction (Plan 02-05).

The plan parser surfaces the optional categoria annotation on the meal block
dict so shopping_service.aggregate_for_week can prefer the explicit hint over
keyword-based mapping (T-02-05-01 STRIDE — bounded user input).
"""

from __future__ import annotations

import pytest

from app.parsers.plan_sections import _extract_category, parse_section

pytestmark = pytest.mark.unit


def test_extract_category_present() -> None:
    body = "Some preamble.\n\n**Categoria:** Frigo & Freschi\n\nBody.\n"
    assert _extract_category(body) == "Frigo & Freschi"


def test_extract_category_absent_returns_none() -> None:
    body = "No annotation here. Just plain text.\n"
    assert _extract_category(body) is None


def test_extract_category_case_insensitive() -> None:
    body = "**categoria:** Dispensa\n"
    assert _extract_category(body) == "Dispensa"


def test_extract_category_strips_whitespace() -> None:
    body = "**Categoria:**   Condimenti   \n"
    assert _extract_category(body) == "Condimenti"


def test_extract_category_empty_string_returns_none() -> None:
    # Body with malformed annotation (no value) should return None — the
    # regex requires at least 1 captured char.
    body = "**Categoria:**\n"
    assert _extract_category(body) is None


def test_extract_category_dropped_when_over_50_chars() -> None:
    # Capture group is `(.{1,50}?)\s*$` — when the user-supplied value exceeds
    # the bound, the line as a whole fails to match and the annotation is
    # silently dropped (fail-safe). shopping_service then falls back to
    # keyword lookup. T-02-05-01 STRIDE mitigation.
    long_value = "X" * 200
    body = f"**Categoria:** {long_value}\n"
    assert _extract_category(body) is None


def test_extract_category_accepts_50_char_value() -> None:
    # 50-char value is exactly at the bound — must extract.
    val = "X" * 50
    body = f"**Categoria:** {val}\n"
    assert _extract_category(body) == val


def test_breakfast_segment_carries_category_annotation() -> None:
    # Real-world style breakfast section using `**Categoria:**`.
    md = """## COLAZIONE

**Categoria:** Frigo & Freschi

| Ingrediente | Quantità | Proteine | Carboidrati | Grassi |
|-------------|----------|----------|-------------|--------|
| Yogurt greco | 200 g | 18 | 8 | 4 |
| TOTALE       |       | 18 | 8 | 4 |

Calorie totali stimate: ~250 kcal
"""
    parsed, _ = parse_section("breakfast", md, heading="COLAZIONE")
    assert parsed is not None
    assert parsed.get("category") == "Frigo & Freschi"


def test_subheading_meal_option_carries_category_annotation() -> None:
    # Subheading format (### Opzione X) — annotation lives inside the option body.
    md = """### Opzione A — Pasta al pomodoro

**Categoria:** Dispensa

| Ingrediente | Quantità |
|-------------|----------|
| Pasta integrale | 80 g |
"""
    parsed, _ = parse_section("lunches", md, heading="PRANZI")
    # Subheading mode emits {default: [opt, opt, ...]}
    assert isinstance(parsed, dict)
    assert "default" in parsed
    options = parsed["default"]
    assert len(options) == 1
    assert options[0]["category"] == "Dispensa"


def test_grid_option_has_no_category_by_default() -> None:
    # Grid format cells don't carry **Categoria:** annotations (they're
    # single-cell text). The category field defaults to None and shopping
    # aggregation falls back to keyword lookup.
    md = """## PRANZI

| Giorno | Opzione A |
|--------|-----------|
| Lun | Pasta al pomodoro |
"""
    parsed, _ = parse_section("lunches", md, heading="PRANZI")
    assert isinstance(parsed, dict)
    assert "lun" in parsed
    assert parsed["lun"][0]["category"] is None
