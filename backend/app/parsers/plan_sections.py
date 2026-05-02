"""Per-section parsers. Phase 1 minimal extraction.

Source: PLAN-02 sections list, RESEARCH Pattern 10 stub `_parse_section`,
        PLAN-01-09 (optional `**Foto:** <url>` extraction for Lifesum-style cards).

Phase 1 strategy:
  * `personal_data` + `macro_target` get regex extraction so the strict schema
    has populated fields downstream.
  * Other sections capture the body verbatim (or as a list-of-dicts wrapper)
    to satisfy the schema's `list[dict]` / `dict[str, list[MealOption]]` shape.
  * Plan 01-09: meal-bearing sections (breakfast / lunches / dinners / snacks)
    OPT-INTO photo_url extraction. The `_extract_photo_url` helper sniffs a
    literal `**Foto:** <url>` line in the body. Absence → photo_url stays None,
    so the existing 6 evil-corpus fixtures (none of which carry photos) keep
    parsing green.
  * Phase 2 will deepen ingredient/quantity extraction + plan editor will
    populate photo_url through the upload flow after sanitization.

The parser emits Phase-1-shaped dicts that match `PlanParsedSchema` field types
(post-`model_validate`).
"""

from __future__ import annotations

import re

_NUMBER_RE = re.compile(r"(\d+(?:[.,]\d+)?)")
# Plan 01-09 — optional photo line "**Foto:** <url>" (case-insensitive, allows
# leading whitespace before the bold marker). Length cap 500 enforced
# downstream by the Pydantic v2 schema and the today_service coercer.
_PHOTO_RE = re.compile(
    r"^\s*\*\*\s*foto\s*:\s*\*\*\s+(\S{1,500})\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)


def _extract_photo_url(body: str) -> str | None:
    """Plan 01-09 — sniff `**Foto:** <url>` line. Returns None when absent."""
    m = _PHOTO_RE.search(body)
    if not m:
        return None
    url = m.group(1).strip()
    return url or None


def _to_float(s: str) -> float | None:
    m = _NUMBER_RE.search(s.replace(",", "."))
    return float(m.group(1)) if m else None


def _to_int(s: str) -> int | None:
    f = _to_float(s)
    return int(f) if f is not None else None


def _parse_personal_data(body: str) -> tuple[dict, list[str]]:
    data: dict = {}
    warnings: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.lstrip("- *").strip()
        low = line.lower()
        if low.startswith("nome"):
            _, _, val = line.partition(":")
            data["name"] = val.strip() or None
        elif low.startswith("età") or low.startswith("eta"):
            _, _, val = line.partition(":")
            data["age"] = _to_int(val)
        elif "peso attuale" in low:
            _, _, val = line.partition(":")
            data["current_weight_kg"] = _to_float(val)
        elif "peso obiettivo" in low or "peso target" in low:
            _, _, val = line.partition(":")
            data["target_weight_kg"] = _to_float(val)
    return data, warnings


def _parse_macros(body: str) -> tuple[dict, list[str]]:
    """Each line is one of kcal / proteine / carboidrati / grassi.

    We check most-specific keyword first to avoid 'kcal' matching a 'proteine' line.
    """
    data: dict = {}
    warnings: list[str] = []
    for line in body.splitlines():
        low = line.lower()
        if not low.strip():
            continue
        # Order matters — match macro keywords before kcal so a macro line containing
        # 'kcal' (rare but possible) doesn't get misclassified.
        if "protein" in low and "protein_g" not in data:
            data["protein_g"] = _to_float(line) or 0
        elif ("carbo" in low or "carboidrat" in low) and "carbs_g" not in data:
            data["carbs_g"] = _to_float(line) or 0
        elif ("grass" in low or "lipid" in low) and "fat_g" not in data:
            data["fat_g"] = _to_float(line) or 0
        elif "kcal" in low and "kcal" not in data:
            data["kcal"] = _to_int(line) or 0
    return data, warnings


def _option_body_segments(body: str) -> list[tuple[str, str]]:
    """Split a meal section's body into [(title_line, segment_body), ...] chunks.

    Each `### TITLE` line begins a new chunk. Lines before the first `###` are
    discarded — Phase 1 doesn't surface preamble. If there are no `###` headings,
    a single (first-non-empty-line, full-body) chunk is returned so per-option
    metadata (e.g. photo_url) can still be sniffed from the section body.
    """
    chunks: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    has_subheading = False
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            has_subheading = True
            if current_title is not None:
                chunks.append((current_title, "\n".join(current_lines)))
            current_title = line[4:].strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)
    if current_title is not None:
        chunks.append((current_title, "\n".join(current_lines)))
    if not has_subheading:
        first_line = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
        chunks.append((first_line or "", body))
    return chunks


def _parse_meal_options(body: str) -> tuple[dict[str, list[dict]], list[str]]:
    """Parse `### Opzione X` chunks under a section.

    Phase 1: keys are "default" + a list of MealOption-shaped dicts. Each `### TITLE`
    becomes one option with `key=TITLE`, `title=TITLE`, and empty ingredients/macros
    (Phase 2 deepens). If no `###` headings present, body becomes a single option.

    Plan 01-09: each option opt-into photo_url via `**Foto:** <url>` line in its
    own segment body — populates the `photo_url` field on the resulting MealOption.
    """
    options: list[dict] = []
    chunks = _option_body_segments(body)
    has_subheading = any(t for t, _b in chunks if t and chunks.index((t, _b)) >= 0)
    # Re-derive has_subheading reliably — chunks always has ≥1 entry; the
    # subheading-flag is true iff `_option_body_segments` populated multiple
    # chunks OR the first chunk's title was set from a `### ...` line. The
    # safest signal: input contains an explicit "### " line.
    has_subheading = any(line.lstrip().startswith("### ") for line in body.splitlines())

    for idx, (title, segment_body) in enumerate(chunks):
        if has_subheading:
            key = title or f"opzione_{idx + 1}"
            display_title = title or "Opzione"
        else:
            key = "default"
            display_title = (title or "Opzione")[:200]
        options.append(
            {
                "key": key,
                "title": display_title,
                "ingredients": [],
                "macros": {},
                "photo_url": _extract_photo_url(segment_body),
            }
        )
    return {"default": options}, []


def _parse_breakfast(body: str) -> tuple[dict | None, list[str]]:
    if not body.strip():
        return None, []
    first_line = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
    return (
        {
            "key": "default",
            "title": (first_line[:200] or "Colazione"),
            "ingredients": [],
            "macros": {},
            "photo_url": _extract_photo_url(body),
        },
        [],
    )


def _parse_snacks(body: str) -> tuple[list[dict], list[str]]:
    first_line = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
    return [
        {
            "key": "default",
            "title": (first_line[:200] or "Spuntino"),
            "ingredients": [],
            "macros": {},
            "photo_url": _extract_photo_url(body),
        }
    ], []


def _parse_raw_lines(body: str) -> tuple[list[str], list[str]]:
    """Used by `rules` (which is `list[str]` per schema)."""
    lines = [ln.lstrip("- *").strip() for ln in body.splitlines() if ln.strip()]
    return lines, []


def _parse_raw_lines_dict(body: str) -> tuple[list[dict], list[str]]:
    """Used by `supplements`/`weight_projection`/`daily_structure` (`list[dict]`)."""
    lines = [ln.lstrip("- *").strip() for ln in body.splitlines() if ln.strip()]
    return [{"raw": line} for line in lines], []


def parse_section(target: str, body: str) -> tuple[object, list[str]]:
    """Dispatch to the right per-section parser. Returns (parsed_value, warnings)."""
    if target == "personal_data":
        return _parse_personal_data(body)
    if target == "macro_target":
        return _parse_macros(body)
    if target == "breakfast":
        return _parse_breakfast(body)
    if target in ("lunches", "dinners"):
        return _parse_meal_options(body)
    if target == "snacks":
        return _parse_snacks(body)
    if target in ("supplements", "weight_projection", "daily_structure"):
        return _parse_raw_lines_dict(body)
    if target == "rules":
        return _parse_raw_lines(body)
    # Fallback — shouldn't happen if SECTION_STEMS dispatch covers all targets.
    return {"raw": body[:500]}, [f"unknown_target_{target}"]
