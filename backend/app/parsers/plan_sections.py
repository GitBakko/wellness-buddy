"""Per-section parsers.

Source: PLAN-02 sections list, RESEARCH Pattern 10 stub `_parse_section`,
        PLAN-01-09 (optional `**Foto:** <url>` extraction for Lifesum-style cards).

Strategy:
  * `personal_data` + `macro_target` use both bullet-list and markdown-table
    extraction so the strict schema downstream gets populated whichever format
    the plan author used.
  * Meal-bearing sections (`breakfast`, `lunches`, `dinners`, `snacks`) parse
    the first ingredient table they find inside each option/segment, summing
    macros from the `TOTALE`/`TOTAL` row and reading the `Calorie totali
    stimate: ~XXX kcal` line below the table.
  * Sections without an ingredient table (DATI PERSONALI, MACRO TARGET,
    STRUTTURA GIORNALIERA, CALCOLO CALORICO) keep their existing extraction.
  * Notes / rules subsections (e.g. `### Note colazione`, `### Regole pasta`)
    are NOT promoted to meal titles — they're either dropped or attached to
    the meal as a `notes` string.
  * Plan 01-09: meal-bearing sections OPT-INTO photo_url extraction via a
    literal `**Foto:** <url>` line inside the segment body.

The parser emits dicts that match `PlanParsedSchema` field types
(post-`model_validate`).
"""

from __future__ import annotations

import re

_NUMBER_RE = re.compile(r"(\d+(?:[.,]\d+)?)")
# Italian thousands separator: a dot between exactly 3-digit groups, e.g. "1.895"
# or "2.000". This must be stripped BEFORE generic number extraction so that
# "~2.000 kcal" parses as 2000, not 2.
_IT_THOUSANDS_RE = re.compile(r"(?<=\d)\.(?=\d{3}(?!\d))")
# Plan 01-09 — optional photo line "**Foto:** <url>" (case-insensitive, allows
# leading whitespace before the bold marker). Length cap 500 enforced
# downstream by the Pydantic v2 schema and the today_service coercer.
_PHOTO_RE = re.compile(
    r"^\s*\*\*\s*foto\s*:\s*\*\*\s+(\S{1,500})\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
# Calorie summary line that follows the breakfast/meal ingredient table:
#   "Calorie totali stimate: ~500 kcal"
_CAL_TOTALI_RE = re.compile(
    r"calorie\s+total[ie]\s+stimate?[^\d~]*~?\s*(\d+(?:[.,]\d+)?)\s*kcal",
    flags=re.IGNORECASE,
)


def _extract_photo_url(body: str) -> str | None:
    """Plan 01-09 — sniff `**Foto:** <url>` line. Returns None when absent."""
    m = _PHOTO_RE.search(body)
    if not m:
        return None
    url = m.group(1).strip()
    return url or None


def _strip_it_thousands(s: str) -> str:
    """Remove Italian thousands separator dots so '1.895' → '1895'."""
    return _IT_THOUSANDS_RE.sub("", s)


def _to_float(s: str) -> float | None:
    cleaned = _strip_it_thousands(s)
    m = _NUMBER_RE.search(cleaned.replace(",", "."))
    return float(m.group(1)) if m else None


def _to_int(s: str) -> int | None:
    f = _to_float(s)
    return int(f) if f is not None else None


# ──────────────────────────────────────────────────────────────────────────────
# Markdown table helpers
# ──────────────────────────────────────────────────────────────────────────────


def _is_table_row(line: str) -> bool:
    """A markdown table row starts and contains at least one '|'."""
    s = line.strip()
    return s.startswith("|") and "|" in s[1:]


def _is_separator_row(cells: list[str]) -> bool:
    """A separator row (`|---|---|`) has only dashes/colons in every cell."""
    if not cells:
        return False
    return all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells if c.strip() != "")


def _split_row(line: str) -> list[str]:
    """Split a `|a|b|c|` row into ['a','b','c']."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [cell.strip() for cell in s.split("|")]


def _extract_tables(body: str) -> list[list[list[str]]]:
    """Return a list of tables, each table a list of rows (cells)."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for raw_line in body.splitlines():
        if _is_table_row(raw_line):
            cells = _split_row(raw_line)
            if _is_separator_row(cells):
                continue  # skip separator
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


# ──────────────────────────────────────────────────────────────────────────────
# DATI PERSONALI
# ──────────────────────────────────────────────────────────────────────────────


_PERSONAL_KEYS = {
    "nome": "name",
    "eta": "age",
    "età": "age",
    "peso attuale": "current_weight_kg",
    "peso iniziale": "current_weight_kg",
    "peso obiettivo": "target_weight_kg",
    "peso target": "target_weight_kg",
}


def _personal_set(data: dict, key_low: str, raw_val: str) -> None:
    """Map a DATI PERSONALI label/value to schema fields."""
    for k_match, schema_key in _PERSONAL_KEYS.items():
        if key_low.startswith(k_match) or k_match in key_low:
            if schema_key == "name":
                data["name"] = raw_val.strip() or None
            elif schema_key == "age":
                data["age"] = _to_int(raw_val)
            else:
                data[schema_key] = _to_float(raw_val)
            return


def _parse_personal_data(body: str) -> tuple[dict, list[str]]:
    data: dict = {}
    warnings: list[str] = []
    # Bullet-list format: "- Nome: Mario" / "- Età: 40"
    for raw_line in body.splitlines():
        line = raw_line.lstrip("- *").strip()
        if not line or _is_table_row(raw_line):
            continue
        if ":" not in line:
            continue
        label, _, val = line.partition(":")
        _personal_set(data, label.strip().lower(), val)
    # Table format: "| Eta | 42 anni |" — first column = label, second = value.
    for table in _extract_tables(body):
        if len(table) < 2:
            continue
        # Skip header row (row 0) — start from row 1
        for row in table[1:]:
            if len(row) < 2:
                continue
            label = row[0].strip().lower()
            val = row[1].strip()
            _personal_set(data, label, val)
    return data, warnings


# ──────────────────────────────────────────────────────────────────────────────
# CALCOLO CALORICO E MACRO TARGET
# ──────────────────────────────────────────────────────────────────────────────


def _macro_classify(label_low: str) -> str | None:
    """Classify a row label into kcal/protein_g/carbs_g/fat_g (or None)."""
    if "protein" in label_low:
        return "protein_g"
    if "carboidrat" in label_low or "carbo" in label_low:
        return "carbs_g"
    if "grass" in label_low or "lipid" in label_low:
        return "fat_g"
    if "target calorico" in label_low or "kcal totali" in label_low:
        return "kcal"
    return None


def _parse_macros(body: str) -> tuple[dict, list[str]]:
    """Extract daily macro targets from bullet-list OR markdown tables.

    Tolerates Italian thousands separator ('~2.000 kcal' → 2000) and 'g' suffix.
    For kcal, prefers explicit 'TARGET CALORICO GIORNALIERO' rows over BMR/TDEE
    lines so the daily target lands in the right bucket.
    """
    data: dict = {}
    warnings: list[str] = []

    # Bullet-list extraction (legacy synthetic plans).
    for line in body.splitlines():
        if _is_table_row(line):
            continue
        low = line.lower()
        if not low.strip():
            continue
        cls = _macro_classify(low)
        if cls and cls not in data:
            if cls == "kcal":
                data["kcal"] = _to_int(line) or 0
            else:
                data[cls] = _to_float(line) or 0
        elif "kcal" not in data and "kcal" in low:
            # Only fall back to a generic kcal line when no explicit target found.
            data["kcal"] = _to_int(line) or 0

    # Table extraction — handle both the calorie summary table and the
    # "Macro giornalieri target" table.
    for table in _extract_tables(body):
        if len(table) < 2:
            continue
        for row in table[1:]:
            if len(row) < 2:
                continue
            label_low = row[0].strip().lower()
            val = row[1].strip()
            cls = _macro_classify(label_low)
            if not cls:
                continue
            if cls == "kcal":
                # Explicit TARGET CALORICO row always wins over a stray bullet match.
                data["kcal"] = _to_int(val) or 0
            elif cls not in data:
                data[cls] = _to_float(val) or 0

    return data, warnings


# ──────────────────────────────────────────────────────────────────────────────
# Meal sections — breakfast, lunches, dinners, snacks
# ──────────────────────────────────────────────────────────────────────────────


_INGREDIENT_HEADER_HINTS = ("ingrediente", "ingredienti", "alimento")
_TOTALE_HINTS = ("totale", "total")
_MACRO_HEADER_HINTS = {
    "protein_g": ("proteine", "proteina", "prot"),
    "carbs_g": ("carbs", "carboidrati", "carbo"),
    "fat_g": ("grassi", "grasso", "lipidi"),
}


def _looks_like_ingredient_table(table: list[list[str]]) -> bool:
    """A table is an ingredient table if its header mentions ingredient/alimento."""
    if not table:
        return False
    header = [c.strip().lower() for c in table[0]]
    if not any(any(h.startswith(hint) for hint in _INGREDIENT_HEADER_HINTS) for h in header):
        return False
    return True


def _macro_column_indices(header: list[str]) -> dict[str, int]:
    """Map macro keys → column index by inspecting the header row."""
    idx_map: dict[str, int] = {}
    low = [c.strip().lower() for c in header]
    for macro_key, hints in _MACRO_HEADER_HINTS.items():
        for i, cell in enumerate(low):
            if any(hint in cell for hint in hints):
                idx_map[macro_key] = i
                break
    return idx_map


def _parse_ingredient_table(table: list[list[str]]) -> tuple[list[dict], dict, str | None]:
    """Parse an ingredient table → (ingredients, totale_macros, totale_kcal_str).

    The TOTALE row carries summed macros. Returns:
      * ingredients: list of {name, quantity, protein_g?, carbs_g?, fat_g?}
      * totale_macros: {protein_g?, carbs_g?, fat_g?} (kcal filled later from
        the "Calorie totali stimate" line that follows the table).
      * totale_kcal_str: kcal cell from the TOTALE row IF the table has a kcal
        column (rare — usually kcal lives on the line below). None otherwise.
    """
    if not table:
        return [], {}, None
    header = table[0]
    macro_cols = _macro_column_indices(header)
    # Detect optional kcal column on the table itself.
    kcal_col: int | None = None
    for i, cell in enumerate([c.strip().lower() for c in header]):
        if "kcal" in cell or "calorie" in cell:
            kcal_col = i
            break
    ingredients: list[dict] = []
    totale_macros: dict = {}
    totale_kcal_str: str | None = None
    for row in table[1:]:
        if not row:
            continue
        first = row[0].strip()
        first_low = first.lower()
        is_total = any(first_low.startswith(h) for h in _TOTALE_HINTS)
        if is_total:
            for macro_key, col_idx in macro_cols.items():
                if col_idx < len(row):
                    val = _to_float(row[col_idx])
                    if val is not None:
                        totale_macros[macro_key] = val
            if kcal_col is not None and kcal_col < len(row):
                totale_kcal_str = row[kcal_col]
            continue
        if not first:
            continue
        # Standard ingredient row: name in col 0, quantity in col 1 (when present),
        # macros in their detected columns.
        ing: dict = {"name": first}
        if len(row) > 1 and row[1].strip():
            ing["quantity"] = row[1].strip()
        for macro_key, col_idx in macro_cols.items():
            if col_idx < len(row):
                val = _to_float(row[col_idx])
                if val is not None:
                    ing[macro_key] = val
        ingredients.append(ing)
    return ingredients, totale_macros, totale_kcal_str


def _segment_body_until_next_subheading(lines: list[str]) -> str:
    """Truncate a meal segment at the first nested heading (### or ####).

    Used so that `### Note colazione` / `### Regole pasta` content does NOT
    get folded into the preceding meal option's body.
    """
    out: list[str] = []
    for line in lines:
        if line.lstrip().startswith("### ") or line.lstrip().startswith("#### "):
            break
        out.append(line)
    return "\n".join(out)


def _is_notes_subheading(title: str) -> bool:
    """Heuristic: a `### Note ...` / `### Regole ...` / `### Avvertenze ...`
    subheading is metadata, not a meal option."""
    low = title.strip().lower()
    return (
        low.startswith("note")
        or low.startswith("regole")
        or low.startswith("avvertenz")
        or low.startswith("tip")
        or low.startswith("ingredienti batch")
        or low.startswith("barrette homemade")
    )


def _clean_meal_title(raw: str, fallback: str) -> str:
    """Strip emoji prefix / parenthetical notes / trailing markers from a heading.

    Examples:
      "COLAZIONE - Post-workout (fissa)" → "Colazione"
      "🍳 COLAZIONE"                      → "Colazione"
      "PRANZI - Piano Settimanale (max 15 minuti)" → "Pranzi"
      "SPUNTINO POMERIGGIO (15:30-16:00) + Elettroliti" → "Spuntino pomeriggio"
    """
    s = raw.strip()
    # Drop leading emoji / non-letter run.
    s = re.sub(r"^[\W_]+", "", s, flags=re.UNICODE)
    # Drop a parenthetical block as soon as it opens (regardless of whether it
    # closes on the same line or after a dash).
    s = re.split(r"\s*\(", s, maxsplit=1)[0]
    # Drop everything from " - " / " — " onward (subtitle / note).
    s = re.split(r"\s+[-–—]\s+", s, maxsplit=1)[0]
    # Drop trailing "+ Elettroliti" style suffixes.
    s = re.split(r"\s+\+\s+", s, maxsplit=1)[0].strip()
    if not s:
        return fallback
    # Title-case for italian: only first letter capitalized, rest lower.
    return s[0].upper() + s[1:].lower()


def _parse_meal_segment(
    title: str,
    segment_body: str,
    key: str,
    *,
    title_fallback: str,
) -> dict:
    """Build a MealOption-shaped dict from one segment body.

    Looks for the first ingredient-style table; if found, extracts ingredients +
    totale macros. Reads the 'Calorie totali stimate: ~XXX kcal' line that
    typically follows the table. Drops intro/`ATTENZIONE:`/`Nota:` paragraphs.
    """
    display_title = _clean_meal_title(title, title_fallback) if title else title_fallback
    ingredients: list[dict] = []
    macros: dict = {}
    notes: str | None = None

    tables = _extract_tables(segment_body)
    ingredient_table = next((t for t in tables if _looks_like_ingredient_table(t)), None)
    if ingredient_table is not None:
        ingredients, totale_macros, totale_kcal_str = _parse_ingredient_table(ingredient_table)
        macros.update(totale_macros)
        if totale_kcal_str:
            kcal_val = _to_int(totale_kcal_str)
            if kcal_val is not None:
                macros["kcal"] = kcal_val

    # Calorie totali stimate line (overrides any totale-row kcal if present).
    cal_match = _CAL_TOTALI_RE.search(segment_body)
    if cal_match:
        macros["kcal"] = int(float(_strip_it_thousands(cal_match.group(1)).replace(",", ".")))

    # Notes — collect lines that look like preamble/postamble paragraphs (not in a table).
    note_lines: list[str] = []
    for raw_line in segment_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _is_table_row(line):
            continue
        # Skip the calorie-summary line — it's already extracted into macros.
        if _CAL_TOTALI_RE.search(line):
            continue
        # Skip nested subheadings entirely (### Note colazione etc.).
        if line.startswith("#"):
            continue
        note_lines.append(line)
    if note_lines:
        joined = " ".join(note_lines).strip()
        if joined:
            notes = joined[:1000]

    return {
        "key": key,
        "title": display_title,
        "ingredients": ingredients,
        "macros": macros,
        "notes": notes,
        "photo_url": _extract_photo_url(segment_body),
    }


def _split_into_segments(body: str) -> list[tuple[str, str]]:
    """Split a section body by `### TITLE` subheadings.

    Returns a list of (title, segment_body). When no subheadings are present,
    returns a single ('', whole body) entry. Subheadings whose title looks
    like notes/rules metadata are filtered out.
    """
    lines = body.splitlines()
    segments: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    has_subheading = False
    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.lstrip()
        if stripped.startswith("### "):
            has_subheading = True
            if current_title is not None:
                segments.append((current_title, "\n".join(current_lines)))
            current_title = stripped[4:].strip()
            current_lines = []
        elif current_title is None:
            current_lines.append(line)
        else:
            current_lines.append(line)
    if current_title is not None:
        segments.append((current_title, "\n".join(current_lines)))

    # Filter out notes/rules subheadings — they're metadata, not meal options.
    filtered = [(t, b) for (t, b) in segments if not _is_notes_subheading(t)]

    if not has_subheading:
        return [("", body)]
    if not filtered:
        # Section had only notes subheadings → fall back to whole body.
        return [("", body)]
    return filtered


def _parse_breakfast(body: str, heading: str = "") -> tuple[dict | None, list[str]]:
    if not body.strip():
        return None, []
    # Breakfast may have a pre-table preamble (ATTENZIONE:..., Nota:...) — those
    # land in `notes`. The title is derived from the section heading.
    title_fallback = "Colazione"
    title = _clean_meal_title(heading, title_fallback) if heading else title_fallback
    # Use the body up to the first `###` (e.g. "### Note colazione") so the
    # ingredient table is the only one considered and notes don't bleed in.
    primary_lines: list[str] = []
    for raw_line in body.splitlines():
        if raw_line.lstrip().startswith("### "):
            break
        primary_lines.append(raw_line)
    primary_body = "\n".join(primary_lines)
    option = _parse_meal_segment(
        title=title,
        segment_body=primary_body,
        key="default",
        title_fallback=title_fallback,
    )
    # Ensure title isn't lost.
    if not option.get("title"):
        option["title"] = title_fallback
    return option, []


def _parse_meal_options(
    body: str, heading: str = "", default_title: str = "Pasto"
) -> tuple[dict[str, list[dict]], list[str]]:
    """Parse `### Opzione X` / `### Variante Y` chunks under a section.

    Returns {"default": [opt1, opt2, ...]}. When no `###` subheadings exist,
    a single 'default' option carries the whole body (so per-option photo_url
    extraction still works).
    """
    options: list[dict] = []
    segments = _split_into_segments(body)
    for idx, (title, segment_body) in enumerate(segments):
        if title:
            # Build a slug-ish key from the title.
            key = _slug(title) or f"opzione_{idx + 1}"
            title_fallback = title
        else:
            key = "default"
            title_fallback = default_title
        opt = _parse_meal_segment(
            title=title,
            segment_body=segment_body,
            key=key,
            title_fallback=title_fallback,
        )
        options.append(opt)
    return {"default": options}, []


def _parse_snacks(body: str, heading: str = "") -> tuple[list[dict], list[str]]:
    """Parse SPUNTINI section — emit a flat list of MealOption dicts.

    Stefano/Marta plans use `## SPUNTINO POMERIGGIO` (a single section with no
    subheadings) and a separate `## SPUNTINO SERALE`. When the body has no
    `###` subheadings, emit a single option keyed by the cleaned heading. When
    it does, each subheading becomes a snack entry.
    """
    snacks: list[dict] = []
    segments = _split_into_segments(body)
    base_title = _clean_meal_title(heading, "Spuntino") if heading else "Spuntino"
    for idx, (title, segment_body) in enumerate(segments):
        if title:
            key = _slug(title) or f"spuntino_{idx + 1}"
            title_fallback = title
        else:
            # No subheadings → treat the whole body as one snack option titled
            # from the parent section heading.
            key = _slug(base_title) or "default"
            title_fallback = base_title
        opt = _parse_meal_segment(
            title=title or base_title,
            segment_body=segment_body,
            key=key,
            title_fallback=title_fallback,
        )
        snacks.append(opt)
    return snacks, []


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(s: str) -> str:
    low = s.strip().lower()
    low = _SLUG_RE.sub("_", low).strip("_")
    return low


# ──────────────────────────────────────────────────────────────────────────────
# Generic helpers (unchanged behavior)
# ──────────────────────────────────────────────────────────────────────────────


def _parse_raw_lines(body: str) -> tuple[list[str], list[str]]:
    """Used by `rules` (which is `list[str]` per schema)."""
    lines = [ln.lstrip("- *").strip() for ln in body.splitlines() if ln.strip()]
    return lines, []


def _parse_raw_lines_dict(body: str) -> tuple[list[dict], list[str]]:
    """Used by `supplements`/`weight_projection`/`daily_structure` (`list[dict]`)."""
    lines = [ln.lstrip("- *").strip() for ln in body.splitlines() if ln.strip()]
    return [{"raw": line} for line in lines], []


# ──────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────────────────────────────────────


def parse_section(target: str, body: str, heading: str = "") -> tuple[object, list[str]]:
    """Dispatch to the right per-section parser. Returns (parsed_value, warnings).

    `heading` is the original `## ...` heading text (without leading hashes);
    breakfast/lunches/dinners/snacks parsers use it to derive clean titles.
    """
    if target == "personal_data":
        return _parse_personal_data(body)
    if target == "macro_target":
        return _parse_macros(body)
    if target == "breakfast":
        return _parse_breakfast(body, heading)
    if target == "lunches":
        return _parse_meal_options(body, heading, default_title="Pranzo")
    if target == "dinners":
        return _parse_meal_options(body, heading, default_title="Cena")
    if target == "snacks":
        return _parse_snacks(body, heading)
    if target in ("supplements", "weight_projection", "daily_structure"):
        return _parse_raw_lines_dict(body)
    if target == "rules":
        return _parse_raw_lines(body)
    # Fallback — shouldn't happen if SECTION_STEMS dispatch covers all targets.
    return {"raw": body[:500]}, [f"unknown_target_{target}"]
