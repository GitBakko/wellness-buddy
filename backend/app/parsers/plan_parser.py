"""Tolerant MD plan parser.

Stem-prefix matching, emoji-prefix tolerant, case-insensitive. Builds a tolerant
intermediate dict from the MD body, then validates strictly via PlanParsedSchema.

Source: PLAN-02, PLAN-04, PLAN-05, PLAN-06, RESEARCH Pattern 10.

Heading-matching algorithm:
  1. Strip leading non-word chars (emoji prefix, " ## ", etc.)
  2. Collapse whitespace + lowercase
  3. Find any `SECTION_STEMS` key that the heading STARTS WITH

This way `"🍳 COLAZIONE"` → stem `"colazione"` → target `"breakfast"`,
and `"CALCOLO CALORICO E MACRO TARGET"` → stem starts with `"calcolo calorico"`
→ target `"macro_target"`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.parsers.normalizer import normalize_md
from app.parsers.plan_sections import parse_section
from app.schemas.plan_parsed import PlanParsedSchema

# Canonical stems (lowercase, accent-insensitive after NFC). Match by stem prefix.
# The dict order matters: longer / more specific stems should come first so
# `"spuntino pomeriggio"` matches before generic `"spuntino"`.
SECTION_STEMS: dict[str, str] = {
    "dati personali": "personal_data",
    "calcolo calorico": "macro_target",  # matches "CALCOLO CALORICO E MACRO TARGET"
    "struttura giornaliera": "daily_structure",
    "colazione": "breakfast",
    "pranzi": "lunches",
    "cene": "dinners",
    "spuntino pomeriggio": "snacks",
    "spuntino": "snacks",  # tolerate "SPUNTINI"/"SPUNTINO"
    "spuntini": "snacks",
    "supplementazione": "supplements",
    "proiezione peso": "weight_projection",
    "regole fondamentali": "rules",
}

_HEADING_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*$", re.MULTILINE)
# Strip a leading run of non-word non-Italian-letter characters (emoji + punctuation).
# `re.UNICODE` ensures `\W` excludes accented Italian letters.
_EMOJI_PREFIX_RE = re.compile(r"^[\W_]+", flags=re.UNICODE)


def _heading_stem(heading_text: str) -> str:
    """Strip emoji prefix, collapse whitespace, lowercase."""
    stripped = _EMOJI_PREFIX_RE.sub("", heading_text)
    return re.sub(r"\s+", " ", stripped).strip().lower()


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Return [(heading_text, body), ...] for every level-2 (`##`) heading.

    Phase 1: only `##` headings count as canonical sections; nested `###`/`####`
    etc. are body content of their parent section.
    """
    parts: list[tuple[str, str]] = []
    matches = list(_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        level = len(m.group(1))
        heading = m.group(2)
        if level != 2:
            continue
        start = m.end()
        # Find next level-2 heading
        end = len(text)
        for nxt in matches[i + 1 :]:
            if len(nxt.group(1)) == 2:
                end = nxt.start()
                break
        parts.append((heading, text[start:end].strip()))
    return parts


@dataclass
class ParseReport:
    """Non-blocking diagnostics emitted by the tolerant parser.

    `unrecognized_headings` is the list of `##` headings that did NOT match any
    canonical stem (PLAN-05). `warnings` accumulates per-section warnings from
    the section-specific parsers.
    """

    warnings: list[str] = field(default_factory=list)
    unrecognized_headings: list[str] = field(default_factory=list)


def _match_target(stem: str) -> str | None:
    """Resolve a heading stem to a canonical target (or None)."""
    # Iterate in declared order; SECTION_STEMS lists the more specific
    # stems first (e.g. "spuntino pomeriggio" before "spuntino").
    for canonical_stem, target in SECTION_STEMS.items():
        if stem.startswith(canonical_stem):
            return target
    return None


def parse_and_validate(raw_bytes: bytes) -> tuple[PlanParsedSchema, ParseReport]:
    """Parse + validate. Tolerant input → strict Pydantic v2 schema.

    Returns (PlanParsedSchema, ParseReport). Raises ValidationError only if the
    parsed structure violates the strict schema (which the section parsers should
    avoid by emitting schema-shaped dicts).
    """
    text = normalize_md(raw_bytes)
    sections = _split_sections(text)
    report = ParseReport()
    raw_dict: dict[str, object] = {}
    for heading, body in sections:
        stem = _heading_stem(heading)
        target = _match_target(stem)
        if target is None:
            report.unrecognized_headings.append(heading)
            continue
        # Skip duplicate sections (Phase 1: first occurrence wins)
        if target in raw_dict:
            report.warnings.append(f"duplicate_section:{target}")
            continue
        parsed_value, sub_warnings = parse_section(target, body)
        raw_dict[target] = parsed_value
        report.warnings.extend(sub_warnings)
    schema = PlanParsedSchema.model_validate(raw_dict)
    return schema, report
