"""Italian quantity parser evil-corpus tests (D-05 + Pattern 3 + Pitfall #14).

Plan 02-05 Task 1 — RED phase.

These tests cover the canonical Italian quantity grammar surfaced by Stefano +
Marta plans:
  * 200g / 1,5 kg / 300 ml — numeric + unit, italian decimal comma
  * q.b. / Q.B. / quanto basta — quanto-basta sentinel (unit='qb', amount=None)
  * un/una/uno + noun — implicit "1 X" (un pizzico → 1 pizzico)
  * 1 confezione / 2 cucchiai — explicit numeric + container/measure unit
  * "+"-joined multi-ingredient lines are exploded into multiple rows
"""

from __future__ import annotations

import pytest

from app.services.ingredient_parser import ParsedIngredient, normalize, parse

EVIL_CASES: list[tuple[str, list[tuple[str, float | None, str | None]]]] = [
    (
        "Yogurt greco 200g + frutta secca 30g + miele 10g",
        [("yogurt greco", 200.0, "g"), ("frutta secca", 30.0, "g"), ("miele", 10.0, "g")],
    ),
    (
        "Pasta integrale 80g + pomodoro + olio EVO",
        [("pasta integrale", 80.0, "g"), ("pomodoro", None, None), ("olio evo", None, None)],
    ),
    (
        "Avena 50g + mirtilli + 1 uovo",
        [("avena", 50.0, "g"), ("mirtilli", None, None), ("uovo", 1.0, None)],
    ),
    (
        "Pesce bianco 150g + zucchine",
        [("pesce bianco", 150.0, "g"), ("zucchine", None, None)],
    ),
    (
        "Mela + 20g noci",
        [("mela", None, None), ("noci", 20.0, "g")],
    ),
    (
        "Olio EVO q.b.",
        [("olio evo", None, "qb")],
    ),
    (
        "Sale q.b.",
        [("sale", None, "qb")],
    ),
    (
        "Un pizzico di sale",
        [("di sale", 1.0, "pizzico")],
    ),
    (
        "Una manciata di basilico",
        [("di basilico", 1.0, "manciata")],
    ),
    (
        "2 cucchiai di olio",
        [("di olio", 2.0, "cucchiai")],
    ),
    (
        "1 confezione di pasta",
        [("di pasta", 1.0, "confezione")],
    ),
    (
        "1,5 kg pomodori",
        [("pomodori", 1.5, "kg")],
    ),
    (
        "300 ml latte",
        [("latte", 300.0, "ml")],
    ),
]


@pytest.mark.parametrize(
    "line,expected",
    EVIL_CASES,
    ids=[c[0][:30] for c in EVIL_CASES],
)
def test_evil_corpus(line: str, expected: list[tuple[str, float | None, str | None]]) -> None:
    result = parse(line)
    actual = [(p.name, p.amount, p.unit) for p in result]
    assert actual == expected


def test_normalize_nfc_lowercase() -> None:
    assert normalize("  YOGURT GRÈCO   200g  ") == "yogurt grèco 200g"


def test_qb_variants_all_normalize_to_qb_unit() -> None:
    for variant in ("q.b.", "q.b", "qb", "QUANTO BASTA"):
        result = parse(f"olio evo {variant}")
        assert len(result) == 1, f"expected single parse for variant {variant!r}"
        assert result[0].unit == "qb"
        assert result[0].amount is None


def test_parse_returns_dataclass_instances() -> None:
    result = parse("pasta 80g")
    assert len(result) == 1
    assert isinstance(result[0], ParsedIngredient)
    assert result[0].name == "pasta"
    assert result[0].amount == 80.0
    assert result[0].unit == "g"


def test_empty_line_returns_empty_list() -> None:
    assert parse("") == []
    assert parse("   ") == []
