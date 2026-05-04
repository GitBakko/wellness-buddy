"""Unit tests for plan_parser tolerant pipeline + evil-corpus parametrized.

Source: PLAN-04, PLAN-05 (warnings non-blocking), PITFALLS #6, T-PARSE-01..03.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.parsers.plan_parser import (
    SECTION_STEMS,
    ParseReport,
    _heading_stem,
    parse_and_validate,
)
from app.schemas.plan_parsed import PlanParsedSchema

pytestmark = pytest.mark.unit

EVIL_DIR = Path("tests/fixtures/plans/evil")
VALID_DIR = Path("tests/fixtures/plans/valid")


def test_parser_extracts_canonical_sections() -> None:
    raw = (VALID_DIR / "stefano_synthetic.md").read_bytes()
    schema, report = parse_and_validate(raw)
    assert isinstance(schema, PlanParsedSchema)
    assert isinstance(report, ParseReport)
    # Personal data extracted
    assert schema.personal_data is not None
    assert schema.personal_data.name == "Stefano"
    assert schema.personal_data.age == 42
    assert schema.personal_data.current_weight_kg == 84.0
    assert schema.personal_data.target_weight_kg == 78.0
    # Macros extracted
    assert schema.macro_target.kcal == 2200
    assert schema.macro_target.protein_g == 165
    assert schema.macro_target.carbs_g == 220
    assert schema.macro_target.fat_g == 75
    # Other sections present (Phase 1 minimal — at least populated)
    assert schema.breakfast is not None
    assert schema.lunches  # truthy dict
    assert schema.dinners
    assert schema.snacks
    assert schema.supplements
    assert schema.weight_projection
    assert schema.rules
    # No unrecognized headings
    assert report.unrecognized_headings == []


def test_parser_case_insensitive() -> None:
    """Lowercase + uppercase headings both match canonical stems."""
    src_lower = "## dati personali\n- Nome: Mario\n- Età: 30\n".encode()
    src_upper = "## DATI PERSONALI\n- Nome: Mario\n- Età: 30\n".encode()
    s_lower, _ = parse_and_validate(src_lower)
    s_upper, _ = parse_and_validate(src_upper)
    assert s_lower.personal_data is not None
    assert s_upper.personal_data is not None
    assert s_lower.personal_data.name == s_upper.personal_data.name == "Mario"


def test_parser_emoji_prefix_stripped() -> None:
    src = "## \U0001f373 COLAZIONE\nYogurt\n".encode("utf-8")
    schema, report = parse_and_validate(src)
    assert schema.breakfast is not None
    assert report.unrecognized_headings == []


def test_parser_unrecognized_section_warning() -> None:
    """PLAN-05: extra sections logged in ParseReport.unrecognized_headings, parsing succeeds."""
    src = b"## DATI PERSONALI\n- Nome: X\n## SEZIONE STRANA\nfoo\n"
    schema, report = parse_and_validate(src)
    assert schema.personal_data is not None
    assert any("STRANA" in h.upper() for h in report.unrecognized_headings)


def test_heading_stem_strips_emoji_and_lowercases() -> None:
    assert _heading_stem("\U0001f373 COLAZIONE") == "colazione"
    assert _heading_stem("DATI PERSONALI") == "dati personali"
    assert _heading_stem("  PRANZI  ") == "pranzi"


def test_section_stems_complete() -> None:
    """Sanity: all canonical Italian sections covered."""
    expected = {
        "personal_data",
        "macro_target",
        "daily_structure",
        "breakfast",
        "lunches",
        "dinners",
        "snacks",
        "supplements",
        "weight_projection",
        "rules",
    }
    assert expected.issubset(set(SECTION_STEMS.values()))


# ──────────────────────────────────────────────────────────────────────────────
# Evil-corpus parametrized — every fixture must parse without crash.
# ──────────────────────────────────────────────────────────────────────────────


EVIL_FIXTURES = sorted(EVIL_DIR.glob("*.md"))


@pytest.mark.parametrize("path", EVIL_FIXTURES, ids=lambda p: p.name)
def test_evil_corpus_parses_without_crash(path: Path) -> None:
    raw = path.read_bytes()
    schema, report = parse_and_validate(raw)
    assert isinstance(schema, PlanParsedSchema)
    # Core invariants on each evil fixture (10 sections crafted in fixtures):
    assert schema.personal_data is not None, f"{path.name}: personal_data not extracted"
    assert schema.macro_target.kcal > 0, f"{path.name}: macro kcal not extracted"
    # All canonical sections matched (no unrecognized headings — every fixture follows the contract).  # noqa: E501
    assert report.unrecognized_headings == [], (
        f"{path.name}: unexpected unrecognized headings: {report.unrecognized_headings}"
    )


def test_evil_word_export_strips_smart_quotes() -> None:
    raw = (EVIL_DIR / "word_export.md").read_bytes()
    schema, _ = parse_and_validate(raw)
    assert schema.personal_data is not None
    assert schema.personal_data.name == "Mario"
    assert schema.macro_target.kcal == 2000


def test_evil_notes_app_nfd_composes() -> None:
    """NFD-decomposed accented chars must round-trip via NFC normalization."""
    raw = (EVIL_DIR / "notes_app_nfd.md").read_bytes()
    schema, _ = parse_and_validate(raw)
    assert schema.macro_target.kcal == 2000


def test_evil_notion_emoji_prefix_matches_all() -> None:
    raw = (EVIL_DIR / "notion_export_emoji.md").read_bytes()
    schema, report = parse_and_validate(raw)
    assert schema.personal_data is not None
    assert schema.personal_data.name == "Sara"
    assert schema.macro_target.kcal == 1800
    assert report.unrecognized_headings == []


def test_evil_obsidian_yaml_frontmatter_ignored() -> None:
    """YAML `---` block at top must NOT confuse `##` heading detection."""
    raw = (EVIL_DIR / "obsidian_export.md").read_bytes()
    schema, report = parse_and_validate(raw)
    assert schema.personal_data is not None
    assert schema.macro_target.kcal == 2200
    assert report.unrecognized_headings == []


def test_evil_notepad_bom_first_heading_clean() -> None:
    """First section heading must NOT be prefixed with U+FEFF after normalization."""
    raw = (EVIL_DIR / "notepad_bom.md").read_bytes()
    assert raw[:3] == b"\xef\xbb\xbf"
    schema, _ = parse_and_validate(raw)
    assert schema.personal_data is not None
    assert schema.personal_data.name == "BOMUser"


def test_evil_nbsp_in_headings_normalizes() -> None:
    """NBSP between heading words must collapse to space so stems match."""
    raw = (EVIL_DIR / "nbsp_in_headings.md").read_bytes()
    schema, report = parse_and_validate(raw)
    assert schema.personal_data is not None
    assert schema.personal_data.name == "NBSPUser"
    assert report.unrecognized_headings == []
