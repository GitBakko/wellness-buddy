"""Per-section parsers.

Source: PLAN-02 sections list, RESEARCH Pattern 10 stub `_parse_section`,
        PLAN-01-09 (optional `**Foto:** <url>` extraction for Lifesum-style cards),
        PLAN 02-04 (weekly grid `| Giorno | Opzione A | Opzione B |` for lunches/dinners).

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
  * Plan 02-04: lunches/dinners DUAL-MODE — try grid format `| Giorno | Opzione A |`
    first (real Stefano + Marta plans). When grid yields ≥1 day key, return
    `{day_slug: [opts]}`. Otherwise fall back to `### Opzione X` subheading
    parsing (EXAMPLE.md backward compat) and return `{'default': [opts]}`.

The parser emits dicts that match `PlanParsedSchema` field types
(post-`model_validate`).
"""

from __future__ import annotations

import re
import unicodedata

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
# Plan 02-05 — optional category annotation line "**Categoria:** <name>"
# (case-insensitive, allows leading whitespace, capture capped at 50 chars to
# bound user-supplied content). Plan author can override the default category
# resolution; downstream aggregation in shopping_service still validates the
# name against the 5-fixed-category list (T-02-05-01 STRIDE mitigation).
_CATEGORY_RE = re.compile(
    r"^\s*\*\*\s*categoria\s*:\s*\*\*\s+(.{1,50}?)\s*$",
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


def _extract_category(body: str) -> str | None:
    """Plan 02-05 — sniff `**Categoria:** <name>` line. Returns None when absent.

    Twin of :func:`_extract_photo_url`. The captured value is bounded by the
    regex (≤50 chars) so a malicious plan author can't blow up downstream
    rendering; shopping_service.aggregate_for_week additionally validates the
    value against the 5 locked categories and falls back to ``"Dispensa"``
    on mismatch.
    """
    m = _CATEGORY_RE.search(body)
    if not m:
        return None
    cat = m.group(1).strip()
    return cat or None


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
        "category": _extract_category(segment_body),
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
    """Dual-mode parser for lunches/dinners (Plan 02-04).

    Mode A (grid format — real Stefano + Marta plans):
      `| Giorno | Opzione A | Opzione B |` → `{lun: [optA, optB], mar: [...]}`.
      day_of_week int list captured per option; key derived from header column.

    Mode B (subheading format — EXAMPLE.md backward compat):
      `### Opzione A — Pasta` chunks → `{'default': [opt1, opt2, ...]}`.
      `day_of_week=None` (week-level).

    Tries grid first; falls back to subheading when grid yields no day keys.
    """
    # Mode A — grid format
    grid_options = _parse_meal_grid(body)
    if grid_options:
        return grid_options, []

    # Mode B — subheading format (existing behavior)
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
        # day_of_week=None → week-level; downstream consumers fall back to 'default' key.
        opt["day_of_week"] = None
        options.append(opt)
    return {"default": options}, []


_SNACK_OPTION_RE = re.compile(
    r"^\s*[-*]\s*(?:opzione\s+([a-d]|\d+)|alt\.\s*([a-d]))\s*:\s*(.+?)\s*$",
    flags=re.IGNORECASE,
)


def _extract_snack_alternatives(body: str) -> list[tuple[str, str]]:
    """Plan 02-05 gap-closure — extract `- Opzione X: <text>` snack alternatives.

    Real Stefano/Marta SPUNTINO POMERIGGIO sections are bullet lists like:
      - Opzione A: 200 g yogurt di soia + 10 g noci
      - Opzione B: 30 g mandorle o noci miste
      - Opzione C: 1 frutto + 20 g noci

    Each `Opzione X:` bullet is an ALTERNATIVE the user picks ONE of — they
    are NOT to be eaten together. This helper returns `[(letter, text), ...]`
    so the caller can emit one MealOption per alternative.

    Returns `[]` when the body has no `Opzione X:` / `Opzione N:` / `Alt. X:`
    bullets so the caller falls back to the legacy single-option behaviour.
    """
    out: list[tuple[str, str]] = []
    for raw_line in body.splitlines():
        m = _SNACK_OPTION_RE.match(raw_line)
        if not m:
            continue
        letter = (m.group(1) or m.group(2) or "").strip().lower()
        text = m.group(3).strip()
        # Drop trailing parenthetical macro hint "(~180 kcal / ~14 g proteine)".
        text = re.split(r"\s*\(~?\s*\d", text, maxsplit=1)[0].strip().rstrip(".,;")
        if not text or not letter:
            continue
        out.append((letter, text[:400]))
    return out


def _split_snack_text_into_ingredients(text: str) -> list[dict]:
    """Split a snack alternative's text on `+` into Ingredient-shaped dicts.

    Mirrors :func:`_split_cell_into_ingredients` (Plan 02-04 grid cells) so
    MealCard renders consistent composition rows whether the source was a
    weekly grid cell OR a snack `Opzione X:` bullet. Returns `[]` for empty
    input; otherwise one row per `+`-separated chunk.
    """
    if not text or not text.strip():
        return []
    parts = [p.strip() for p in text.split("+") if p.strip()]
    out: list[dict] = []
    for part in parts:
        clean = part.strip().rstrip(".,;")
        if not clean:
            continue
        out.append({"name": clean[:200]})
    return out


def _parse_snacks(body: str, heading: str = "") -> tuple[list[dict], list[str]]:
    """Parse SPUNTINI section — emit a flat list of MealOption dicts.

    Stefano/Marta plans use `## SPUNTINO POMERIGGIO` (a single section with no
    subheadings) and a separate `## SPUNTINO SERALE`. When the body has no
    `###` subheadings, emit a single option keyed by the cleaned heading. When
    it does, each subheading becomes a snack entry.

    Plan 02-05 gap-closure: when the section body has `- Opzione X: <text>`
    bullets (real plan format), each bullet is an ALTERNATIVE the user picks
    one of — emit ONE MealOption PER bullet. Title becomes `<Section> -
    Opzione X` so the user clearly sees they're alternatives. Ingredients are
    split on `+` matching the grid-cell convention.
    """
    base_title = _clean_meal_title(heading, "Spuntino") if heading else "Spuntino"
    base_slug = _slug(base_title) or "spuntino"

    # Plan 02-05 gap-closure: detect `Opzione X:` bullets at the section level
    # BEFORE splitting into subheading segments. When present, emit one option
    # per alternative and skip the legacy single-option path entirely.
    alternatives = _extract_snack_alternatives(body)
    if alternatives:
        return _build_snack_alternatives(
            alternatives,
            base_title=base_title,
            base_slug=base_slug,
            full_body=body,
        ), []

    # Legacy / backward-compat path: snack body has no `Opzione X:` bullets.
    snacks: list[dict] = []
    segments = _split_into_segments(body)
    for idx, (title, segment_body) in enumerate(segments):
        if title:
            key = _slug(title) or f"spuntino_{idx + 1}"
            title_fallback = title
        else:
            # No subheadings → treat the whole body as one snack option titled
            # from the parent section heading.
            key = base_slug or "default"
            title_fallback = base_title
        opt = _parse_meal_segment(
            title=title or base_title,
            segment_body=segment_body,
            key=key,
            title_fallback=title_fallback,
        )
        snacks.append(opt)
    return snacks, []


def _build_snack_alternatives(
    alternatives: list[tuple[str, str]],
    *,
    base_title: str,
    base_slug: str,
    full_body: str,
) -> list[dict]:
    """Plan 02-05 gap-closure — emit one MealOption per `Opzione X:` bullet.

    Each alternative becomes a fully-formed MealOption-shaped dict with:
      * `key = "<base_slug>__opzione_<letter>"` (stable for variant lookup)
      * `title = "<Base title> - Opzione <LETTER-UPPER>"`
      * `ingredients` split on `+` (matches grid-cell convention)
      * `macros = {}` — proportional allocation done in today_service /
        weekly_service so each option carries its full section share.
      * `notes`, `photo_url`, `category` — extracted from the SECTION body so
        a `**Foto:** <url>` line attaches to all alternatives uniformly.
    """
    photo_url = _extract_photo_url(full_body)
    category = _extract_category(full_body)
    out: list[dict] = []
    for letter, text in alternatives:
        ingredients = _split_snack_text_into_ingredients(text)
        out.append(
            {
                "key": f"{base_slug}__opzione_{letter}",
                "title": f"{base_title} - Opzione {letter.upper()}"[:200],
                "ingredients": ingredients,
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                "notes": None,
                "photo_url": photo_url,
                "category": category,
            }
        )
    return out


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(s: str) -> str:
    low = s.strip().lower()
    low = _SLUG_RE.sub("_", low).strip("_")
    return low


# Plan 02-04 gap-closure — grid header columns that should NOT become variants.
# Real Stefano + Marta plans add helper columns (Note, Porzione Marta, Extra Stefano)
# that aren't user-selectable alternatives — they're either annotations or
# partner-specific portion sizes. Filter them by header slug prefix.
_NON_VARIANT_HEADERS = (
    "note",
    "porzione_",  # Porzione Marta, Porzione Stefano
    "extra_",  # Extra Stefano, Extra Marta
    "macro_",  # "Macro Marta" column on dinners table
    "kcal",
    "calorie",
)


def _is_non_variant_header(header_slug: str) -> bool:
    """True for grid header columns that are annotations, not variant choices."""
    return any(header_slug.startswith(prefix) for prefix in _NON_VARIANT_HEADERS)


# ──────────────────────────────────────────────────────────────────────────────
# Plan 02-04 — weekly grid (`| Giorno | Opzione A | Opzione B |`) parser
# ──────────────────────────────────────────────────────────────────────────────

# Italian day-of-week mapping. 0=Mon..6=Sun (matches Python date.weekday()).
# Multiple aliases per day so `Lun`/`Lunedi`/`Lunedì`/`LUNEDÌ` all match the
# same int. Accents stripped via NFD normalization before lookup.
_DAY_TO_INT: dict[str, int] = {
    "lun": 0,
    "lunedi": 0,
    "mar": 1,
    "martedi": 1,
    "mer": 2,
    "mercoledi": 2,
    "gio": 3,
    "giovedi": 3,
    "ven": 4,
    "venerdi": 4,
    "sab": 5,
    "sabato": 5,
    "dom": 6,
    "domenica": 6,
}

_INT_TO_DAY_SLUG: dict[int, str] = {
    0: "lun",
    1: "mar",
    2: "mer",
    3: "gio",
    4: "ven",
    5: "sab",
    6: "dom",
}

# Separators that may join multiple day labels in a single cell:
#   "Lun / Gio", "Lun-Gio", "Lun, Gio", "Lun & Gio", "Lun&Gio".
_DAY_SEP_RE = re.compile(r"[/,&\-]+")

# Header detector for the weekly grid. Case-insensitive match on the first
# column being "Giorno" / "Giorni" / "Giorno" with optional accents/whitespace.
_GRID_HEADER_RE = re.compile(r"^\s*giorn[oi]\s*$", re.IGNORECASE)


def _strip_accents(s: str) -> str:
    """NFD-normalize and drop combining marks so 'Lunedì' → 'lunedi'."""
    nfd = unicodedata.normalize("NFD", s)
    return "".join(c for c in nfd if not unicodedata.combining(c))


def _parse_day_label(label: str) -> list[int]:
    """Map an Italian day-label cell to a sorted list of day_of_week ints (0..6).

    Accepts short ("Lun"), full ("Lunedì"), accented or not, joined by `/`, `,`,
    `&`, or `-`. Returns `[]` when no token matches a known day (so caller can
    skip rows like "TOTALE" or "Note").
    """
    if not label or not label.strip():
        return []
    normalized = _strip_accents(label).lower().strip()
    tokens = [tok.strip() for tok in _DAY_SEP_RE.split(normalized) if tok.strip()]
    days: set[int] = set()
    for tok in tokens:
        if tok in _DAY_TO_INT:
            days.add(_DAY_TO_INT[tok])
    return sorted(days)


def _grid_variant_key_from_header(header_label: str, idx: int) -> str:
    """Derive a stable variant key from a grid header cell.

    Examples:
      "Opzione A"      → "opzione_a"
      "Opzione B"      → "opzione_b"
      "Piatto"         → "piatto" (single-column grids)
      ""               → "opzione_{idx+1}" (defensive fallback)
    """
    slug = _slug(header_label)
    return slug or f"opzione_{idx + 1}"


def _split_cell_into_ingredients(cell_text: str) -> list[dict]:
    """Plan 02-04 gap-closure — split a grid cell into Ingredient-shaped dicts.

    Real Stefano/Marta cells use `+` as the canonical separator between
    ingredients, e.g. `"3 uova strapazzate + 80 g riso basmati + insalata"` →
    three ingredients. Each part becomes one Ingredient row with both `name`
    and free-form display set to the trimmed text. Per-ingredient quantity
    parsing is deferred to Phase 2 (the schema's `quantity` field is optional).

    Returns `[]` when the cell is empty or doesn't contain meaningful text.
    """
    if not cell_text or not cell_text.strip():
        return []
    # Drop leading "Libero" / "—" placeholder cells.
    parts = [p.strip() for p in cell_text.split("+") if p.strip()]
    if not parts:
        return []
    ingredients: list[dict] = []
    for part in parts:
        # Strip trailing punctuation / parentheticals (e.g. "(15:30-16:00)").
        clean = part.strip().rstrip(".,;")
        if not clean:
            continue
        ingredients.append({"name": clean[:200]})
    return ingredients


def _build_grid_option(
    *,
    title: str,
    key: str,
    day_of_week: list[int],
) -> dict:
    """Schema-shaped MealOption dict for a single grid cell.

    Plan 02-04 gap-closure:
      * `ingredients` is now populated by splitting the cell text on `+`.
        Real Stefano/Marta cells encode their composition inline (e.g.
        `"200 g salmone + 200 g patate + verdura saltata"`).
      * `macros` stay zero here — proportional allocation against the daily
        macro_target happens downstream in today_service / weekly_service so
        the per-meal totals add up to the plan's daily kcal target.
    """
    return {
        "key": key,
        "title": title.strip()[:200],
        "ingredients": _split_cell_into_ingredients(title),
        "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
        "notes": None,
        "photo_url": None,
        "day_of_week": day_of_week,
        "category": None,
    }


def _parse_meal_grid(body: str) -> dict[str, list[dict]]:
    """Parse a weekly grid (`| Giorno | Opzione A | Opzione B |`) into day-keyed options.

    Returns `{day_slug: [MealOption-dict, ...]}`. Empty dict when no grid header
    is found OR no data row maps to a known day. Caller can detect "no grid" and
    fall back to subheading parsing.

    Grid contract:
      * Header row's first cell matches `Giorno` (case-insensitive)
      * Subsequent rows: first cell = day label (Lun/Lunedi/Lun-Gio/...);
        remaining cells = variant cells (one MealOption per non-empty cell)
      * Rows where the day label parses to `[]` are skipped
      * TOTALE / TOTAL rows from ingredient tables are intentionally NOT a
        valid day-label, so they're skipped too.
    """
    grid: dict[str, list[dict]] = {}
    tables = _extract_tables(body)
    target_table: list[list[str]] | None = None
    header_cells: list[str] = []
    for table in tables:
        if not table:
            continue
        header = [c.strip() for c in table[0]]
        if not header:
            continue
        # Match the first column as some form of "Giorno"/"Giorni"
        if _GRID_HEADER_RE.match(header[0]):
            target_table = table
            header_cells = header
            break
    if target_table is None:
        return {}

    # Derive variant keys from header columns 1..N. Plan 02-04 gap-closure:
    # filter non-variant helper columns (Note, Porzione Marta, Extra Stefano,
    # Macro Marta, kcal/calorie) so they don't pollute the variant selector.
    variant_headers_raw = header_cells[1:]
    variant_indices: list[int] = []
    variant_keys: list[str] = []
    for i, h in enumerate(variant_headers_raw):
        slug = _slug(h)
        if _is_non_variant_header(slug):
            continue
        variant_keys.append(_grid_variant_key_from_header(h, i))
        variant_indices.append(i)

    if not variant_keys:
        # All helper columns? Fall back to using every column except the day cell.
        variant_indices = list(range(len(variant_headers_raw)))
        variant_keys = [
            _grid_variant_key_from_header(h, i) for i, h in enumerate(variant_headers_raw)
        ]

    for row in target_table[1:]:
        if not row:
            continue
        first = row[0].strip()
        days = _parse_day_label(first)
        if not days:
            # Row whose first cell isn't a recognised day label — skip.
            continue
        cells = row[1:]
        for variant_pos, col_idx in enumerate(variant_indices):
            if col_idx >= len(cells):
                break
            cell_text = cells[col_idx].strip()
            if not cell_text:
                continue
            variant_key = variant_keys[variant_pos]
            option = _build_grid_option(
                title=cell_text,
                key=variant_key,
                day_of_week=list(days),
            )
            for d in days:
                slug = _INT_TO_DAY_SLUG[d]
                grid.setdefault(slug, []).append(option)
    return grid


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
