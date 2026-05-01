"""Per-section parsers. Phase 1 minimal extraction.

Source: PLAN-02 sections list, RESEARCH Pattern 10 stub `_parse_section`.

Phase 1 strategy:
  * `personal_data` + `macro_target` get regex extraction so the strict schema
    has populated fields downstream.
  * Other sections capture the body verbatim (or as a list-of-dicts wrapper)
    to satisfy the schema's `list[dict]` / `dict[str, list[MealOption]]` shape.
  * Phase 2 will deepen ingredient/quantity extraction.

The parser emits Phase-1-shaped dicts that match `PlanParsedSchema` field types
(post-`model_validate`).
"""

from __future__ import annotations

import re

_NUMBER_RE = re.compile(r"(\d+(?:[.,]\d+)?)")


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


def _parse_meal_options(body: str) -> tuple[dict[str, list[dict]], list[str]]:
    """Parse `### Opzione X` chunks under a section.

    Phase 1: keys are "default" + a list of MealOption-shaped dicts. Each `### TITLE`
    becomes one option with `key=TITLE`, `title=TITLE`, and empty ingredients/macros
    (Phase 2 deepens). If no `###` headings present, body becomes a single option.
    """
    options: list[dict] = []
    current: dict | None = None
    has_subheading = False
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            has_subheading = True
            title = line[4:].strip()
            current = {
                "key": title or f"opzione_{len(options) + 1}",
                "title": title or "Opzione",
                "ingredients": [],
                "macros": {},
            }
            options.append(current)
        elif current is not None:
            if line.strip():
                # Append body lines to title for now (Phase 2 promotes to ingredients)
                current["title"] = current["title"]  # keep title; body deferred
    if not has_subheading:
        # Single-option fallback
        first_line = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
        options.append(
            {
                "key": "default",
                "title": (first_line or "Opzione")[:200],
                "ingredients": [],
                "macros": {},
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
