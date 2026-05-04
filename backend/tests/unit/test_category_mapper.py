"""Category mapper tests (D-07 + Pattern 3 — 5 fixed Italian categories).

Plan 02-05 Task 1 — RED phase.

The 5-category lock per D-07:
    Frigo & Freschi / Frutta & Verdura / Dispensa / Condimenti / Integratori
Default fallback for unknown ingredients is 'Dispensa'.
"""

from __future__ import annotations

import pytest

from app.services.category_mapper import CATEGORY_ORDER, lookup


@pytest.mark.parametrize(
    "name,expected",
    [
        # Frigo & Freschi
        ("yogurt greco", "Frigo & Freschi"),
        ("yogurt 0%", "Frigo & Freschi"),
        ("salmone affumicato", "Frigo & Freschi"),
        ("uova", "Frigo & Freschi"),
        # Frutta & Verdura
        ("pomodoro", "Frutta & Verdura"),
        ("pomodorini ciliegino", "Frutta & Verdura"),
        ("mela rossa", "Frutta & Verdura"),
        ("noci sgusciate", "Frutta & Verdura"),
        # Dispensa
        ("pasta integrale", "Dispensa"),
        ("riso basmati", "Dispensa"),
        ("avena", "Dispensa"),
        ("miele millefiori", "Dispensa"),
        # Condimenti — order matters: "olio evo" must beat "olio"
        ("olio evo", "Condimenti"),
        ("olio extravergine d'oliva", "Condimenti"),
        ("aceto balsamico", "Condimenti"),
        ("sale fino", "Condimenti"),
        # Integratori
        ("vitamina d3", "Integratori"),
        ("magnesio", "Integratori"),
        ("omega 3", "Integratori"),
        # Default fallback (D-07)
        ("ingrediente sconosciuto xyz", "Dispensa"),
        ("", "Dispensa"),
    ],
)
def test_lookup(name: str, expected: str) -> None:
    assert lookup(name) == expected


def test_category_order_locked() -> None:
    assert CATEGORY_ORDER == [
        "Frigo & Freschi",
        "Frutta & Verdura",
        "Dispensa",
        "Condimenti",
        "Integratori",
    ]


def test_lookup_strips_whitespace_and_is_case_insensitive() -> None:
    assert lookup("  YOGURT GRECO  ") == "Frigo & Freschi"
    assert lookup("Pasta Integrale") == "Dispensa"
