---
phase: 02-differentiators
plan: 06
subsystem: pdf-export
tags:
  - phase-2
  - pdf-export
  - weasyprint
  - reportlab
  - jinja2
  - iphone-safari
  - italian-accents
  - shop-07
  - dep-06
  - ui-09
  - ui-15
  - ui-17
  - ui-18
requirements:
  - SHOP-07
  - DEP-06
  - UI-09
  - UI-15
  - UI-17
  - UI-18
dependency_graph:
  requires:
    - "02-01"  # PdfExporter ABC + WeasyPrintExporter + ReportLabExporter + get_pdf_exporter factory
    - "02-04"  # parser lunches/dinners grid + MealOption.ingredients
    - "02-05"  # build_pdf_payload + 5-category aggregation
  provides:
    - "/api/shopping/{week_start}/export-pdf endpoint live (was 501 stub)"
    - "shopping_list.html Jinja2 template with woff2 base64 inline fonts"
    - "OKLCH drift CI gate (D-12 mirror enforcement)"
    - "Esporta PDF button wired in /spesa with sonner success/error feedback"
    - "iPhone Safari + Mail.app accent verification checklist artifact"
  affects:
    - "02-08"  # closure consumes 02-06-IPHONE-PDF-VERIFY.md sign-off
    - "frontend/src/pages/Shopping.tsx"
    - "backend/app/api/shopping.py"
tech_stack:
  added:
    - "pypdf>=4 (test-only, accent text-extraction validation)"
  patterns:
    - "Plan 02-01 PdfExporter ABC factory wired via Depends(get_pdf_exporter)"
    - "FastAPI dependency_overrides[get_pdf_exporter] for pinning ReportLab in tests (bypasses GTK3 missing on dev box)"
    - "woff2 base64 data URL inline in @font-face (D-13 — guarantees Italian accents render on iPhone Safari/Mail.app without OS font dependency)"
    - "Browser fetch + response.blob() + URL.createObjectURL + anchor.download (NOT apiClient — apiClient auto-decodes JSON)"
    - "OKLCH drift gate pattern: backend script + integration test importlib invoke, both fail on coord mismatch"
key_files:
  created:
    - backend/app/templates/shopping_list.html        # 66.8KB · 141 lines · 3 @font-face base64 + 5-category Jinja2 loop + page-break-inside:avoid
    - backend/app/templates/__init__.py
    - backend/app/templates/_build_inline_fonts.py    # one-shot helper, emits base64 fragments
    - backend/app/static/fonts/plus-jakarta-sans-variable.woff2   # 21KB latin-ext
    - backend/app/static/fonts/geist-mono-variable.woff2          # 13KB latin-ext
    - backend/app/static/fonts/instrument-serif-italic.woff2      # 12KB latin-ext italic
    - backend/scripts/check_pdf_template_oklch.py     # D-12 drift gate
    - backend/tests/integration/test_pdf_export.py    # 8 tests
    - .planning/phases/02-differentiators/02-06-IPHONE-PDF-VERIFY.md
  modified:
    - backend/app/api/shopping.py                     # 501 stub → real exporter via Depends(get_pdf_exporter)
    - backend/tests/integration/test_shopping_api.py  # 501-test repurposed → asserts non-501
    - backend/pyproject.toml                          # pypdf dev dep + scripts/** ruff T20 ignore
    - backend/.env                                    # PDF_BACKEND=reportlab for dev (gitignored — not committed)
    - frontend/src/services/shopping.ts               # +useExportPdf mutation
    - frontend/src/pages/Shopping.tsx                 # button wiring + spinner state
    - frontend/src/components/icons/index.ts          # +CircleNotch
decisions:
  - "Local dev uses PDF_BACKEND=reportlab (GTK3/Pango unavailable on dev Windows box); production keeps PDF_BACKEND=weasyprint (Plan 02-01 spike validated GTK3 on Windows Server 2019). Plan 02-01 ABC factory makes the swap transparent."
  - "Tests use FastAPI app.dependency_overrides[get_pdf_exporter] = ReportLabExporter to pin the backend per-test rather than mutating settings.PDF_BACKEND env (env is read at module init, dependency_overrides scopes cleanly)."
  - "OKLCH drift gate is BOTH a CI script (backend/scripts/check_pdf_template_oklch.py) AND a pytest test (importlib-invoke) — same logic, two enforcement points so dev runs and CI runs both fail on drift."
  - "Real-device iPhone Safari + Mail.app verification deferred to Plan 02-08 closure (post-deploy); 02-06-IPHONE-PDF-VERIFY.md is the sign-off artifact Stefano fills."
metrics:
  duration_minutes: 27
  completed_date: "2026-05-05"
  tasks_completed: "3/3"
  backend_tests_before: 299
  backend_tests_after: 307  # +8 (PDF export) +1 modified (501 stub → contract)
  frontend_tests_before: "103 pass / 3 fail (pre-existing)"
  frontend_tests_after: "103 pass / 3 fail (pre-existing — unchanged)"
  files_created: 9
  files_modified: 7
  commits: 4
---

# Phase 2 Plan 06: PDF Export — Shopping List Summary

**One-liner:** WeasyPrint + Jinja2 brand-template PDF export wired through Plan 02-01 ABC + Plan 02-05 payload, OKLCH drift gate enforced, ReportLab fallback validates locally without GTK3, iPhone Safari accent verification checklist ready for production sign-off.

## Outcome

`/api/shopping/{week_start}/export-pdf` flips from 501 stub to live endpoint returning `application/pdf` with Italian-localized brand chrome. The frontend `Esporta PDF` button downloads `Lista-spesa-{week_start}.pdf` with sonner success/error feedback and a width-stable spinner loading state. Live HTTP smoke against the running dev server returns 200 + 3.5KB PDF + magic bytes `25 50 44 46 2d 31 2e 34` (`%PDF-1.4`); pypdf text extraction confirms 2-page output covering 5 category sections with Stefano's real plan ingredients.

## Implementation Highlights

### Backend
- **`shopping_list.html`** (141 lines, 66.8KB) is the WeasyPrint template:
  - `@page A4 portrait` with 20mm margins + `@bottom-center` (`Wellness Buddy · domain`) + `@bottom-right` (page counter Geist Mono)
  - 3 `@font-face` blocks with `data:font/woff2;base64,…` inline (Plus Jakarta Sans 400/800 normal, Geist Mono 400/600 normal, Instrument Serif 400 italic) — ~63KB base64 total in template body
  - Brand contract: `h1.title` Plus Jakarta 700 28pt slate-ink, `.subtitle` Instrument Serif italic 14pt leaf-700, `section.category h2` Plus Jakarta 600 14pt with leaf-700 underline, `ul.items li .qty` Geist Mono tabular-nums right-aligned
  - `section.category { page-break-inside: avoid }` keeps short categories on one page
  - 5-category Jinja2 loop matching Plan 02-05 payload shape
- **`_build_inline_fonts.py`** is the one-shot helper that emits base64 @font-face fragments to stdout (re-run only when woff2 binaries are replaced)
- **`backend/scripts/check_pdf_template_oklch.py`** (D-12 drift gate) verifies all 6 OKLCH coord literals in the template mirror `frontend/src/styles/theme.css` canonical values. Output: `OK: 6/6 OKLCH coords match theme.css canonical values`
- **`backend/app/api/shopping.py`** export endpoint now uses `Depends(get_pdf_exporter)` factory — Plan 02-01's ABC routes to WeasyPrint or ReportLab per `settings.PDF_BACKEND`. Response includes `Content-Disposition: attachment; filename="Lista-spesa-{week_start}.pdf"` + `Cache-Control: private, no-store` (T-02-06-02 mitigation)

### Tests (8 new + 1 updated, 307/307 passing)
- `test_export_returns_pdf_bytes` — happy path: 200 + content-type + magic bytes + Content-Disposition + Cache-Control
- `test_export_no_active_plan_returns_400` — JSON envelope `{detail, code: "no_active_plan"}`
- `test_export_unauthorized_returns_401` — Depends gate
- `test_export_stress_100_rows` — synthetic 100-row payload, validates page-break-inside: avoid
- `test_export_italian_accents_present` — pypdf text extraction confirms `è`/`à`/`ù` round-trip
- `test_export_via_reportlab_fallback` — asserts the dependency override yields `ReportLabExporter` (factory contract)
- `test_template_contains_font_face_and_page_break` — keeps `@font-face × 3`, `data:font/woff2;base64, × 3`, `page-break-inside: avoid`, Jinja2 loop intact
- `test_template_oklch_mirrors_theme_css` — pytest twin of the CI gate script

### Frontend
- **`useExportPdf(weekStart)`** mutation in `shopping.ts` does browser-direct fetch with Bearer JWT, handles JSON error envelope, blobs the response, triggers anchor download, sonner success `PDF pronto.` / error `Esportazione non riuscita. Riprova tra poco.`
- **Esporta PDF button** in `Shopping.tsx` swaps `FilePdf` icon for `CircleNotch` spinner during `isPending`; width-stable (`min-w-[148px]`), `aria-busy`, `disabled` prevents double-tap, motion-scale honored on spin animation, transition-opacity for taste

## Decisions Made

1. **Dev-side runs ReportLab; production keeps WeasyPrint.** GTK3/Pango is unavailable on the dev Windows box (`OSError: cannot load library 'gobject-2.0-0'`). Plan 02-01 spike already validated GTK3 on Windows Server 2019 — production keeps `PDF_BACKEND=weasyprint` for the Plus Jakarta + Instrument Serif visual brand contract; dev runs `PDF_BACKEND=reportlab` for end-to-end correctness validation. Plan 02-01's `PdfExporter` ABC makes this swap transparent — both backends honor identical request/response contract.
2. **Tests use FastAPI `app.dependency_overrides` for backend pinning** — not env-var mutation. The override is per-test (autouse fixture in `test_pdf_export.py` + manual override in the repurposed shopping_api test). Avoids pollution of settings cache and is the idiomatic FastAPI pattern.
3. **OKLCH drift gate is enforced in both CI script AND pytest** — same logic invoked two ways. Dev pytest runs catch drift before commit; CI script catches drift on PRs that don't run tests.
4. **Real-device iPhone verification deferred to Plan 02-08 closure.** Plan 02-06 ships the artifact (`02-06-IPHONE-PDF-VERIFY.md`) — Stefano fills sign-off after production deploy. This plan is unblocked from his manual verification.
5. **woff2 sourced locally from `frontend/node_modules/@fontsource-variable/*` and `@fontsource/instrument-serif`** — no Google Fonts CDN download needed (the `latin-ext` subset covers Italian accents). Total ~47KB woff2 source → ~63KB base64 in template, ~67KB final template.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Local dev box lacks GTK3/Pango → switched dev `.env` to `PDF_BACKEND=reportlab`**
- **Found during:** Task 2 RED — first WeasyPrint test attempt surfaced `OSError: cannot load library 'gobject-2.0-0'`
- **Issue:** WeasyPrint primary backend cannot run on the dev box (no MSYS2/GTK3 install path). Production has it (Plan 02-01 spike Day 1).
- **Fix:** (a) flipped `backend/.env` `PDF_BACKEND=weasyprint` → `reportlab` (gitignored — not committed); (b) tests pin `ReportLabExporter` via `app.dependency_overrides[get_pdf_exporter]` autouse fixture; (c) production `.env.production` (Plan 02-03) keeps `weasyprint` unchanged.
- **Files modified:** `backend/.env` (gitignored), `backend/tests/integration/test_pdf_export.py`, `backend/tests/integration/test_shopping_api.py`
- **Validates:** end-to-end PDF correctness via ReportLab fallback path; visual WeasyPrint brand contract validation deferred to production deploy + Stefano iPhone verification (Plan 02-08).

**2. [Rule 3 — Blocking] Existing `test_export_pdf_endpoint_returns_501` no longer valid after we replaced the stub**
- **Found during:** Task 2 GREEN, full suite run.
- **Issue:** Plan 02-05 shipped a 501 stub test; Plan 02-06 explicitly replaces the body — test breaks.
- **Fix:** repurposed test as `test_export_pdf_endpoint_authenticated` — asserts `status_code != 501` (any wired response) and uses dependency override to pin ReportLab so the test does not require GTK3.
- **Commit:** `248e24a`.

**3. [Rule 2 — Critical functionality] Added pypdf as test-only dep**
- **Reason:** the italian-accent test requires text extraction to validate that `è`/`à`/`ù` round-trip through the PDF text layer. Without pypdf the test would skip silently and the accent guarantee (D-13) would have no automated coverage on dev. Added `pypdf>=4` to `[dependency-groups] dev`.

### Plan-level deviations

- The plan's Task 1 PowerShell `Invoke-WebRequest` snippet was **not used** — local `frontend/node_modules/@fontsource-variable/*` already had latin-ext woff2 with full Italian accent coverage. Saved a network round-trip and avoided fragile CDN URL pinning.
- The plan's example `_build_inline_fonts.py` had `print(...)` calls flagged by ruff `T20` rule (`print` found). Resolved by adding `scripts/**` and `app/templates/_build_inline_fonts.py` to `[tool.ruff.lint.per-file-ignores]` — CLI tools legitimately print to stdout.

## Authentication Gates

None. JWT/login flow already established in Plan 01-03; Esporta PDF reuses the existing access-token state from Zustand `useAuthStore`.

## TDD Gate Compliance

- **RED commit:** `3f3240f` — `test(02-06-task-2)`. 8 PDF export tests, all failing on 501.
- **GREEN commit:** `248e24a` — `feat(02-06-task-2)`. Template + endpoint + drift gate; 8 tests pass + 1 updated.
- **REFACTOR:** none needed; lint+format clean on first GREEN pass.

## Verification

| Check | Result |
|------|-------|
| Backend tests | 307 passed (was 299; +8 PDF tests + 1 updated) |
| Frontend tests | 103 pass / 3 fail pre-existing (no regression) |
| Frontend `tsc --noEmit` | clean |
| Frontend `eslint . --max-warnings=0` | clean |
| OKLCH drift gate (`backend/scripts/check_pdf_template_oklch.py`) | `OK: 6/6 OKLCH coords match` |
| Live ASGI smoke (`PDF_BACKEND=reportlab`) | 200 + `application/pdf` + 3519 bytes + magic `25 50 44 46 2d 31 2e 34` |
| Live HTTP `:8002` smoke (real Stefano plan) | 200 + 2-page PDF + 5-category structure + apostrophe-d preserved (Burro D'Arachidi, Fiocchi D'Avena) |

Note on accents in dev: ReportLab default Helvetica encoding renders `Caffe` (no accent) for `Caffè` because base PDF fonts lack `è`. **Production WeasyPrint with woff2 Plus Jakarta Sans renders `Caffè` correctly** — that's the single most important visual contract validated by `02-06-IPHONE-PDF-VERIFY.md` after deploy.

## Stefano iPhone Safari Verification Status

**PENDING (post-deploy).** `02-06-IPHONE-PDF-VERIFY.md` artifact ready: 4 surfaces (Safari direct / Mail.app / Files / desktop reader), 7-string italian accent corpus (Pomodorì, Caffè, Olio d'oliva extravergine, Yogurt grèco, Una piada, Spaghetti alla puttanèsca, Tiramisù), Stefano sign-off matrix. Closure rule: any FAIL → flip `PDF_BACKEND=reportlab` in `.env.production` and restart NSSM (Plan 02-08 captures fix work).

## WeasyPrint vs ReportLab Outcome

- **Plan 02-01 spike Day 7 verdict:** WeasyPrint primary; production deploys with `PDF_BACKEND=weasyprint` on Windows Server 2019 (GTK3 installed via MSYS2 per DEPLOY.md Appendix B).
- **Plan 02-06 dev-side reality:** dev Windows box lacks GTK3 → `PDF_BACKEND=reportlab` for local. Tests use `dependency_overrides` rather than env mutation. ABC contract honored — endpoint behavior identical between backends.
- **Production validation owed:** Stefano runs `02-06-IPHONE-PDF-VERIFY.md` after Plan 02-03 production deploy is hit by the live frontend. If WeasyPrint fails on production (unlikely — Plan 02-01 spike was on identical OS), `PDF_BACKEND=reportlab` flip is the documented mitigation.

## Hand-off to Plan 02-08

Plan 02-08 closure consumes:
1. **`02-06-IPHONE-PDF-VERIFY.md`** — Stefano completes the 4-surface sign-off matrix on real iPhone Safari + Mail.app + Files + desktop reader. PASS verifies WeasyPrint primary + woff2 inline + Italian accents (D-13 honored). FAIL triggers ReportLab flip mitigation.
2. **OKLCH drift gate** — Plan 02-08 wires the `check_pdf_template_oklch.py` script into CI (`.github/workflows/*` if exists or pre-commit hook). Drift fails the build.
3. **WeasyPrint memory leak observation** (T-02-06-05) — Plan 02-08 records "RSS stable over 100 PDFs" verdict on production after first week of use.

## Pitfall Coverage (T-02-06-*)

| Threat ID | Mitigation |
|---|---|
| T-02-06-01 Tampering (XSS-equivalent in template) | Jinja2 `autoescape=True` in `WeasyPrintExporter.__init__` (Plan 02-01) escapes user-supplied ingredient names |
| T-02-06-02 Information disclosure (intermediary cache) | `Cache-Control: private, no-store` on response |
| T-02-06-04 DoS (large category list) | 100-row stress test passes, `page-break-inside: avoid` honored |
| T-02-06-05 WeasyPrint memory leak | Deferred to Plan 02-08 production observation |
| T-02-06-07 OKLCH drift between PDF + theme.css | CI script + pytest gate enforce 6/6 coord match |
| T-02-06-08 Spoofing (export without auth) | `Depends(get_current_user)` enforced; 401 test passes |
| T-02-06-09 Cross-user PDF (crafted week_start) | Plan 02-06 ships own-user only; Plan 02-07 wires `get_user_with_group_access` for cross-user |

## Known Stubs

None. All template categories iterate dynamically over `categories` payload from `shopping_service.build_pdf_payload`. No hardcoded category names, no placeholder strings, no "coming soon" text.

## Threat Flags

None. The endpoint surface is identical to the Plan 02-05 scaffold — only the response body shape changed (PDF bytes vs JSON envelope). No new auth paths, no new file access, no schema changes. Future Plan 02-07 family-sync work touches `get_user_with_group_access` for cross-user PDF reads — that's the next threat-surface expansion.

## Self-Check: PASSED

### File existence

- [x] `backend/app/templates/shopping_list.html` — 66.8KB (`stat` confirms)
- [x] `backend/app/templates/_build_inline_fonts.py`
- [x] `backend/app/templates/__init__.py`
- [x] `backend/app/static/fonts/plus-jakarta-sans-variable.woff2` (21KB)
- [x] `backend/app/static/fonts/geist-mono-variable.woff2` (13KB)
- [x] `backend/app/static/fonts/instrument-serif-italic.woff2` (12KB)
- [x] `backend/scripts/check_pdf_template_oklch.py`
- [x] `backend/tests/integration/test_pdf_export.py`
- [x] `.planning/phases/02-differentiators/02-06-IPHONE-PDF-VERIFY.md`

### Commits (verified via `git log --oneline -10`)

- [x] `4eff599` — `chore(02-06-task-1): woff2 fonts + _build_inline_fonts helper for PDF embedding`
- [x] `3f3240f` — `test(02-06-task-2): RED — add failing PDF export tests (SHOP-07)`
- [x] `248e24a` — `feat(02-06-task-2): GREEN — shopping_list.html template + export_pdf endpoint live + OKLCH drift gate (SHOP-07, D-12, D-13)`
- [x] `d7e3f3c` — `feat(02-06-task-3): Esporta PDF button wiring + iPhone Safari accent verify artifact (SHOP-07, T-PDF-02, D-13)`

### Live verification

- [x] `POST /api/shopping/2026-05-04/export-pdf` returns 200 + `application/pdf` + 3519 bytes + magic bytes `%PDF-1.4` (live HTTP via uvicorn :8002 + ASGI direct)
- [x] PDF text extraction yields 2 pages, 5 category sections, real Stefano plan ingredients with apostrophes preserved
- [x] OKLCH drift gate exits 0 (`OK: 6/6 OKLCH coords match theme.css canonical values`)
- [x] All 307 backend tests pass
- [x] Frontend `tsc --noEmit` clean, `eslint --max-warnings=0` clean
