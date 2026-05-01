"""Unit tests for backend/app/parsers/normalizer.py — Plan 04 Task 1.

Source: PLAN-03, PITFALLS #6 (utf-8-sig BOM trap).

Pipeline: utf-8-sig decode → CRLF→LF → NFC → NBSP→space → smart-punct→ASCII.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest

from app.parsers.normalizer import normalize_md

pytestmark = pytest.mark.unit

EVIL_DIR = Path("tests/fixtures/plans/evil")


def test_normalize_strips_bom() -> None:
    """utf-8-sig decode must drop the leading UTF-8 BOM (PITFALLS #6)."""
    text = normalize_md(b"\xef\xbb\xbf# Test")
    # No leading BOM character (U+FEFF) survives.
    assert not text.startswith("﻿")
    assert text == "# Test"


def test_normalize_crlf_to_lf() -> None:
    text = normalize_md(b"a\r\nb\r\nc")
    assert text == "a\nb\nc"
    assert "\r" not in text


def test_normalize_lone_cr_to_lf() -> None:
    text = normalize_md(b"a\rb\rc")
    assert text == "a\nb\nc"
    assert "\r" not in text


def test_normalize_nfc() -> None:
    """Decomposed Unicode (NFD) → composed (NFC). 'café' stable across forms."""
    nfd = unicodedata.normalize("NFD", "café")
    assert nfd != "café"  # sanity: NFD differs byte-wise
    text = normalize_md(nfd.encode("utf-8"))
    assert text == "café"
    assert unicodedata.is_normalized("NFC", text)


def test_normalize_nbsp_to_space() -> None:
    # U+00A0 NBSP → ASCII space
    text = normalize_md("a b".encode("utf-8"))
    assert text == "a b"


def test_normalize_smart_quotes() -> None:
    """Curly single + double quotes → straight ASCII."""
    text = normalize_md("“hello” ‘world’".encode("utf-8"))
    assert text == '"hello" \'world\''


def test_normalize_em_dash() -> None:
    text = normalize_md("foo—bar".encode("utf-8"))
    assert text == "foo-bar"


def test_normalize_en_dash() -> None:
    text = normalize_md("foo–bar".encode("utf-8"))
    assert text == "foo-bar"


def test_normalize_ellipsis() -> None:
    text = normalize_md("loading…".encode("utf-8"))
    assert text == "loading..."


def test_normalize_evil_word_export_roundtrip() -> None:
    """Read word_export.md fixture and assert all evil traps removed after normalization."""
    raw = (EVIL_DIR / "word_export.md").read_bytes()
    assert b"\r\n" in raw  # sanity: fixture truly has CRLF
    text = normalize_md(raw)
    assert "\r" not in text
    assert "—" not in text  # em-dash gone
    assert "“" not in text and "”" not in text  # smart quotes gone


def test_normalize_evil_notepad_bom_strips() -> None:
    raw = (EVIL_DIR / "notepad_bom.md").read_bytes()
    assert raw[:3] == b"\xef\xbb\xbf"
    text = normalize_md(raw)
    assert not text.startswith("﻿")
    assert text.startswith("# Piano BOM")


def test_normalize_evil_notes_nfd_composes() -> None:
    raw = (EVIL_DIR / "notes_app_nfd.md").read_bytes()
    text = normalize_md(raw)
    # After NFC: "città è perché" composed
    assert "città è perché" in text
    assert unicodedata.is_normalized("NFC", text)


def test_normalize_evil_nbsp_to_space() -> None:
    raw = (EVIL_DIR / "nbsp_in_headings.md").read_bytes()
    assert b"\xc2\xa0" in raw  # sanity: NBSP byte-pair present in fixture
    text = normalize_md(raw)
    assert " " not in text  # NBSP gone
    assert "DATI PERSONALI" in text  # heading reads cleanly
