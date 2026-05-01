"""Markdown text normalization pipeline. Source: PLAN-03, PITFALLS #6.

Pipeline: utf-8-sig decode → CRLF→LF → NFC → NBSP→space → smart-punct→ASCII.

CRITICAL (PITFALLS #6): `utf-8-sig` decodes WITH BOM stripping; `utf-8` does NOT.
Notepad on Windows often saves files with a leading EF BB BF BOM; failing to strip
it leaves a U+FEFF "zero-width no-break space" prefixed to the first heading,
which breaks tolerant heading-stem matching downstream.
"""

from __future__ import annotations

import re
import unicodedata

# NBSP variants: U+00A0 (no-break space), U+2007 (figure space),
# U+202F (narrow no-break space), U+2060 (word joiner — zero-width but binds words).
_NBSP_REGEX = re.compile(r"[   ⁠]")

_SMART_QUOTE_MAP = str.maketrans(
    {
        "‘": "'",  # left single quote
        "’": "'",  # right single quote
        "‚": "'",  # single low-9 quote
        "‛": "'",  # single high-reversed-9 quote
        "“": '"',  # left double quote
        "”": '"',  # right double quote
        "„": '"',  # double low-9 quote
        "‟": '"',  # double high-reversed-9 quote
        "–": "-",  # en dash
        "—": "-",  # em dash
        "…": "...",  # horizontal ellipsis
    }
)


def normalize_md(raw_bytes: bytes) -> str:
    """Normalize MD bytes to clean parseable text.

    Steps (order matters):
      1. Decode as utf-8-sig (strips leading BOM if present).
      2. CRLF / lone CR → LF.
      3. Unicode NFC composition (Apple Notes / iOS often emits NFD).
      4. NBSP variants → ASCII space.
      5. Smart quotes / dashes / ellipsis → ASCII.

    Returns the normalized text (never raises on malformed bytes — uses errors='replace').
    """
    text = raw_bytes.decode("utf-8-sig", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFC", text)
    text = _NBSP_REGEX.sub(" ", text)
    text = text.translate(_SMART_QUOTE_MAP)
    return text
