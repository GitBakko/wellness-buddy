"""Italian recipe quantity parser (D-05, Plan 02-05 Pattern 3).

Inputs are short ingredient strings from MD plans (e.g. ``Yogurt greco 200g``,
``mela e 20g noci``, ``pasta integrale 80g + pomodoro + olio EVO q.b.``).
Output is a list of ``ParsedIngredient(name, amount, unit)`` rows.

Strategy (heuristic, deterministic, no NLP):
  1. Normalize: NFC + lowercase + strip + collapse whitespace.
  2. Split candidate boundaries on `` + `` or ``,`` (one row may carry multiple
     ingredients; the caller then explodes one row → many).
  3. For each candidate: scan with a prioritized regex set (longest unit first
     to avoid ``g`` matching inside ``gnocchi``).
  4. Words remaining after amount/unit removal = ingredient name.
  5. Special tokens: ``q.b.`` / ``q.b`` / ``qb`` / ``quanto basta`` → unit
     ``"qb"``, amount ``None``.
  6. ``un`` / ``una`` / ``uno`` BEFORE a measure noun → amount=1, unit=noun
     (``un pizzico`` → ``(1, "pizzico")``).

Out of scope for Phase 2 (D-06):
  * Fuzzy ingredient matching (``pomodorini`` ≠ ``pomodori``).
  * Synonym dictionary (Phase 5 AI).
  * Cross-language unit conversion (g ↔ kg ↔ oz).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# Order matters: longest first, otherwise ``g`` swallows ``gr`` swallows
# ``grammi``.
_UNITS_LONG_FIRST: tuple[str, ...] = (
    "grammi",
    "gr",
    "kg",
    "g",
    "ml",
    "cl",
    "litro",
    "litri",
    "l",
    "cucchiai",
    "cucchiaio",
    "cucchiaini",
    "cucchiaino",
    "tazza",
    "tazze",
    "pizzico",
    "pizzichi",
    "manciata",
    "manciate",
    "fetta",
    "fette",
    "spicchio",
    "spicchi",
    "mazzo",
    "mazzi",
    "confezione",
    "confezioni",
    "bustina",
    "bustine",
    "lattina",
    "lattine",
    "barattolo",
    "barattoli",
    "pezzo",
    "pezzi",
    "foglia",
    "foglie",
)

_UNIT_RE = re.compile(
    r"(?P<amount>\d+(?:[.,]\d+)?)\s*(?P<unit>" + "|".join(_UNITS_LONG_FIRST) + r")\b",
    flags=re.IGNORECASE,
)
_QB_RE = re.compile(r"\bq\.?\s?b\.?(?!\w)|\bquanto\s+basta\b", flags=re.IGNORECASE)
_UN_RE = re.compile(
    r"\b(?:un|una|uno)\s+(?P<unit>pizzico|manciata|fetta|spicchio|mazzo|cucchiaio|cucchiaino)\b",
    flags=re.IGNORECASE,
)
_NUMERIC_PREFIX_RE = re.compile(r"^\s*(?P<amount>\d+(?:[.,]\d+)?)\s+(?P<rest>.+)$")


@dataclass(frozen=True)
class ParsedIngredient:
    """Single (name, amount, unit) row produced by :func:`parse`.

    ``unit`` is ``"qb"`` for quanto-basta items (no amount); ``None`` when no
    measure unit was detected. ``amount`` is ``None`` for q.b. and free-form
    items.
    """

    name: str
    amount: float | None
    unit: str | None


def normalize(s: str) -> str:
    """NFC + lowercase + strip + collapse internal whitespace."""
    s = unicodedata.normalize("NFC", s)
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def parse(line: str) -> list[ParsedIngredient]:
    """Parse one ingredient line into one-or-more ``ParsedIngredient`` rows.

    A line carrying multiple ingredients separated by ``+`` or ``,`` is
    exploded into multiple rows (e.g. ``"yogurt 200g + miele 10g"`` returns
    two rows). Empty / whitespace-only input returns an empty list.
    """
    norm = normalize(line)
    if not norm:
        return []

    # Split candidates on " + " or " , " (whitespace-separated comma) — a bare
    # comma without surrounding whitespace is treated as a decimal separator
    # (e.g. ``1,5 kg pomodori`` stays a single ingredient row).
    parts = [p.strip(" -*•") for p in re.split(r"\s*\+\s*|\s+,\s+|,\s+", norm) if p.strip(" -*•")]
    out: list[ParsedIngredient] = []
    for part in parts:
        out.append(_parse_single(part))
    return out


def _parse_single(part: str) -> ParsedIngredient:
    # 1. quanto basta — explicit "qb" sentinel
    if _QB_RE.search(part):
        name = _QB_RE.sub("", part).strip(" -*•")
        return ParsedIngredient(name=name, amount=None, unit="qb")

    # 2. amount + unit (e.g. "200g", "1 confezione", "2 cucchiai")
    m = _UNIT_RE.search(part)
    if m:
        amount = float(m.group("amount").replace(",", "."))
        unit = _normalize_unit(m.group("unit"))
        name = (part[: m.start()] + part[m.end() :]).strip(" -*•")
        return ParsedIngredient(name=name, amount=amount, unit=unit)

    # 3. "un pizzico", "una manciata" (no digit, "un/una/uno" + measure noun)
    m = _UN_RE.search(part)
    if m:
        unit = _normalize_unit(m.group("unit"))
        name = _UN_RE.sub("", part).strip(" -*•")
        return ParsedIngredient(name=name, amount=1.0, unit=unit)

    # 4. Bare numeric prefix without unit (rare but seen in plans: "2 mele", "1 uovo")
    m = _NUMERIC_PREFIX_RE.match(part)
    if m:
        return ParsedIngredient(
            name=m.group("rest").strip(" -*•"),
            amount=float(m.group("amount").replace(",", ".")),
            unit=None,
        )

    # 5. No quantity detected — return as plain name
    return ParsedIngredient(name=part.strip(" -*•"), amount=None, unit=None)


# Canonical-form lookup: collapse plural/singular and synonymous abbreviations
# to a single canonical token so aggregation in shopping_service buckets
# (canonical_name, unit) keys cleanly.
_UNIT_CANON: dict[str, str] = {
    "grammi": "g",
    "gr": "g",
    "g": "g",
    "kg": "kg",
    "litro": "l",
    "litri": "l",
    "l": "l",
    "ml": "ml",
    "cl": "cl",
    "cucchiaio": "cucchiai",
    "cucchiai": "cucchiai",
    "cucchiaino": "cucchiaini",
    "cucchiaini": "cucchiaini",
    "tazza": "tazze",
    "tazze": "tazze",
    "pizzico": "pizzico",
    "pizzichi": "pizzico",
    "manciata": "manciata",
    "manciate": "manciata",
    "fetta": "fette",
    "fette": "fette",
    "spicchio": "spicchi",
    "spicchi": "spicchi",
    "mazzo": "mazzi",
    "mazzi": "mazzi",
    "confezione": "confezione",
    "confezioni": "confezione",
    "bustina": "bustine",
    "bustine": "bustine",
    "lattina": "lattine",
    "lattine": "lattine",
    "barattolo": "barattoli",
    "barattoli": "barattoli",
    "pezzo": "pezzi",
    "pezzi": "pezzi",
    "foglia": "foglie",
    "foglie": "foglie",
}


def _normalize_unit(raw: str) -> str:
    return _UNIT_CANON.get(raw.lower(), raw.lower())
