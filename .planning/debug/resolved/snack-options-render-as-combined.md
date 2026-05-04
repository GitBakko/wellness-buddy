---
status: investigating
trigger: "snack section OPZIONE A/B/C/D bullets render as combined ingredient list instead of alternative choices"
created: 2026-05-04T00:00:00Z
updated: 2026-05-04T00:00:00Z
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "_parse_snacks collapses `- Opzione X:` bullets into one MealOption.ingredients via _extract_snack_bullet_ingredients. Frontend MealCard renders ingredients[] as a combined `ul`, so user sees the 4 alternatives as a single must-eat-all list."
  confirming_evidence:
    - "plan_sections.py:597-618 — _extract_snack_bullet_ingredients regex matches `Opzione X:` bullets and emits {name: <text>} ingredient dicts"
    - "plan_sections.py:655-656 — _parse_snacks attaches bullet_ingredients to opt['ingredients'] when title='' and table absent"
    - "plans/PIANO_NUTRIZIONALE_STEFANO.md:107-115 — real plan body has 4 `- Opzione X:` bullets under `## SPUNTINO POMERIGGIO`"
    - "MealCard.tsx:106-129 — renders meal.ingredients as flat `ul` with `·` bullet — no alternative semantics"
  falsification_test: "If _parse_snacks already emitted multiple MealOptions for `Opzione X:` bullets, the snack list would have len>1 per section and frontend would show separate cards. Empirically (user report + code reading) only 1 MealOption per section is created."
  fix_rationale: "Schema-stable change: change parser semantic from 'bullets are ingredients of one option' to 'bullets are alternative options'. Each `- Opzione X: <text>` becomes its own MealOption with title `<Section> - Opzione X` and ingredients split on `+`. today_service snack-pool split must group by base section so each alternative carries the FULL section share (user picks one). Frontend can stay minimal: each card is titled clearly as `Opzione X` so the user sees alternatives, OR group into one card with chip-row (better UX). Will start with minimum approach (titled cards), upgrade to grouped if straightforward."
  blind_spots:
    - "weekly_service uses strict 4-slot-per-day model — snack[0] is selected by variant_key. With 4 snack options for pomeriggio + 1 for serale, only ONE snack appears per weekly day. Need to confirm /weekly still works."
    - "Existing test_today_returns_active_plan_meals_for_today fixture has 1 snack with explicit kcal=280 → still passes (raw_macros wins). My split-by-section change only affects per-snack target when raw_macros.kcal=0."
    - "frontend MealCard test may have assumptions about ingredient rendering that change with the title-based approach."

test: TDD — write failing parser test for Stefano POMERIGGIO body expecting 4 distinct MealOptions; then today_service split test grouped by section.
expecting: parser produces 4 MealOption (Opzione A..D) for `## SPUNTINO POMERIGGIO` with titles `Spuntino pomeriggio - Opzione A..D`, ingredients split on `+`. today_service groups by base section: 2 sections × 5% each → 100 kcal per option (when daily=2000).
next_action: Write failing tests in backend/tests/unit/parsers/test_snack_options.py and backend/tests/unit/services/test_today_snack_split.py.

## Symptoms

expected: For a snack section with `- Opzione A:..`, `- Opzione B:..` etc., the user must CHOOSE ONE alternative. UI should present alternatives clearly.
actual: All 4 lines listed as if every line is to be eaten together (4-line ingredient list under one snack title in MealCard).
errors: none — semantic/parsing bug, not crash.
reproduction: Stefano plan body with `## SPUNTINO POMERIGGIO (15:30-16:00) + Elettroliti` followed by 4 `- Opzione X: ...` bullets; visit /today or /settimana, observe single MealCard with combined ingredients.
started: ongoing — parser was written assuming snacks have flat ingredient bullets.

## Eliminated

(none yet — root cause is well-understood from user prompt; this is an executable fix task)

## Evidence

- timestamp: 2026-05-04T00:00:00Z
  checked: User prompt describing parser behavior
  found: _parse_snacks calls _extract_snack_bullet_ingredients which collapses `Opzione X` bullets into a single MealOption.ingredients list
  implication: Need to detect `Opzione X:` bullet pattern and emit MULTIPLE MealOption per snack section

## Resolution

root_cause: Parser `_parse_snacks` collapsed `- Opzione X: <text>` alternatives into a single MealOption.ingredients list via `_extract_snack_bullet_ingredients`. Frontend MealCard renders ingredients as a flat `ul`, so the 4 alternatives appeared as a single must-eat-all list.
fix: |
  Backend parser: `_parse_snacks` now detects `Opzione X:` bullets at the section level (≥1 occurrence) and emits ONE MealOption per bullet with:
    * key = `<base_slug>__opzione_<x>` (e.g. `spuntino_pomeriggio__opzione_a`)
    * title = `<Base title> - Opzione <LETTER>` so the user clearly sees alternatives
    * ingredients = bullet text split on `+` (matches grid-cell convention)
    * macros = zero (proportional allocation done downstream)
  When the body has no `Opzione X:` bullets, the legacy single-option path is used (backward compat).

  Backend today_service: snack-pool macro split now groups by base section key (extracted via `_snack_base_section_key` which strips `__opzione_<x>` suffix). 2 sections × 5% = 100 kcal per option for a 2000 kcal target (every option in a section carries the FULL section share, since the user picks one alternative).

  Minimum frontend approach taken: cards stay separate but each card title now reads `Spuntino pomeriggio - Opzione A/B/C/D`, making the alternative semantics visible. No frontend code changes required.
verification: |
  * 12 new unit tests pass (`tests/unit/parsers/test_snack_options.py` + `tests/unit/services/test_today_snack_split.py`)
  * Full backend suite 280/280 green
  * Live `GET /api/today` (after re-parsing the active plan via `app.parsers.plan_parser.parse_and_validate` + commit) returns 5 snack entries: 4 `Spuntino pomeriggio - Opzione A..D` (each ingredients split, kcal=100) + 1 `Spuntino serale` (kcal=100). Math: 5% × 2000 × 2 sections = 200 kcal total snack pool ✓
  * Frontend pre-existing failures (PlanDiffView, WorkoutForm i18n) confirmed unrelated by stash-test on master.
files_changed:
  - backend/app/parsers/plan_sections.py
  - backend/app/services/today_service.py
  - backend/tests/unit/parsers/test_snack_options.py (new)
  - backend/tests/unit/services/test_today_snack_split.py (new)
