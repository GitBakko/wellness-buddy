---
phase: 02-differentiators
plan: 01
subsystem: pdf-export
tags:
  - phase-2
  - weasyprint
  - reportlab
  - gtk3
  - spike
  - windows-server-2019
  - pdf
  - dep-06
dependency_graph:
  requires:
    - phase-1 backend service-layer pattern (`backend/app/services/__init__.py`)
    - phase-1 settings + Pydantic v2 BaseSettings (`backend/app/core/config.py`)
    - AI provider ABC analog (`backend/app/ai/factory.py`) — same shape extended for PDF
  provides:
    - "`PdfExporter` ABC + `WeasyPrintExporter` (D-11 primary) + `ReportLabExporter` (D-14 fallback) + `get_pdf_exporter` factory"
    - "`settings.PDF_BACKEND` env-keyed flip ('weasyprint' | 'reportlab') — runtime dispatch without code change"
    - "DEPLOY.md Appendix B: 5-section MSYS2 + Pango install recipe for Windows Server 2019"
    - "GTK3 spike scaffold (`02-01-GTK3-SPIKE.md`) — Day 0 install matrix + 7-day continuous logging + verdict + Stefano sign-off"
  affects:
    - "Plan 02-05 PDF endpoint will `Depends(get_pdf_exporter)` to obtain active backend per request"
    - "Plan 02-03 deploy walkthrough now includes GTK3 install (DEPLOY.md Appendix B replaces Section 12 deferral note)"
    - "Plan 02-07 closure cannot pass until Stefano fills the 7-day spike sign-off"
tech_stack:
  added:
    - weasyprint==62.3
    - reportlab==4.5.0
    - jinja2==3.1.6
    - apscheduler==3.11.2
  patterns:
    - lazy-import-on-method (defensive against missing GTK3 DLLs at module-load time)
    - forgiving factory (unknown env value falls through to primary, never crashes startup)
    - spike-as-artifact (7-day stability check tracked in repo, not informally)
key_files:
  created:
    - backend/app/services/pdf_export.py
    - backend/tests/unit/test_pdf_export_factory.py
    - .planning/phases/02-differentiators/02-01-GTK3-SPIKE.md
  modified:
    - backend/pyproject.toml
    - backend/uv.lock
    - backend/app/core/config.py
    - backend/.env.example
    - DEPLOY.md
decisions:
  - "PdfExporter ABC scaffolds both backends; PDF_BACKEND=weasyprint default. Day 7 verdict by Stefano flips to reportlab if 5xx ≥2% (D-11)."
  - "Lazy `from weasyprint import HTML` inside method body (NOT module top) — keeps test envs without GTK3 healthy and mitigates T-02-01-06 (DLL-load DoS)."
  - "Forgiving factory: unknown PDF_BACKEND values fall through to WeasyPrint (T-02-01-05 mitigation — never crash startup on env tampering/typo)."
  - "Mypy override extended to weasyprint.* and reportlab.* (no upstream stubs; ignore_missing_imports follows existing passlib/jose pattern)."
  - "DEPLOY.md Appendix B replaces Section 12 (Phase 1 deferral note) as the canonical install recipe."
metrics:
  duration: ~25 min
  completed_date: 2026-05-02
  tasks_completed: 2
  tasks_total: 2
  files_changed: 8 (3 created + 5 modified)
  commits: 2
  tests_before: 134
  tests_after: 139
---

# Phase 2 Plan 01: WeasyPrint GTK3 Spike Kit + PdfExporter ABC Summary

PdfExporter ABC scaffolded with WeasyPrint primary + ReportLab fallback behind a single env-keyed factory; 7-day GTK3 stability spike opens for Stefano on Windows Server 2019.

## What was built

**Two atomic commits on `worktree-agent-a2c1d93746e865c3d`:**

1. `c5c01f2` — `chore(02-01): WeasyPrint dependencies + GTK3 spike checklist + DEPLOY.md Appendix B (DEP-06)`
2. `bd91e65` — `feat(02-01): PdfExporter ABC + WeasyPrint primary + ReportLab fallback + PDF_BACKEND setting (DEP-06, D-11..D-14)`

### Dependencies installed (locked in `backend/uv.lock`)

| Package | Version | Purpose |
|---------|---------|---------|
| weasyprint | 62.3 | D-11 primary PDF renderer (HTML+CSS → PDF). Requires GTK3/Pango on Windows Server. |
| reportlab | 4.5.0 | D-14 fallback PDF renderer. Pure-Python, no GTK3 dependency. |
| jinja2 | 3.1.6 | HTML template engine for `WeasyPrintExporter` (Plan 02-05 ships `shopping_list.html`). |
| apscheduler | 3.11.2 | Phase 2 weekly shopping reset cron (D-09); Phase 3 push reminders. Installed once. |

`uv sync --frozen` succeeds — 98 packages resolved.

### Code surface

`backend/app/services/pdf_export.py` (new, 156 lines):

```python
class PdfExporter(ABC):
    @abstractmethod
    async def render_shopping_list(*, week_start, week_start_long_it, domain, categories) -> bytes: ...

class WeasyPrintExporter(PdfExporter):
    def __init__(self, template_dir: Path) -> None:
        from jinja2 import Environment, FileSystemLoader  # lazy
        ...

    async def render_shopping_list(self, *, ...) -> bytes:
        from weasyprint import HTML  # lazy — keeps test envs without GTK3 healthy
        ...

class ReportLabExporter(PdfExporter):
    async def render_shopping_list(self, *, ...) -> bytes:
        from reportlab.... # lazy
        ...

def get_pdf_exporter() -> PdfExporter:
    backend = (settings.PDF_BACKEND or "weasyprint").lower()
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    if backend == "reportlab":
        return ReportLabExporter()
    return WeasyPrintExporter(template_dir=template_dir)
```

`backend/app/core/config.py` — adds `PDF_BACKEND: str = Field(default="weasyprint", ...)` after the existing `AI_PROVIDER` field (mirrors Phase 1 settings pattern).

`backend/.env.example` — documents `PDF_BACKEND=weasyprint` with the flip-to-reportlab note tied to Plan 02-01 spike outcome.

### DEPLOY.md Appendix B (6 sub-sections)

Appended after Section 16 (supersedes the Phase 1 Section 12 deferral note):

- **B.1** — Install MSYS2 (one-time, `C:\msys64`)
- **B.2** — `pacman -S mingw-w64-x86_64-pango` inside MSYS2 MINGW64 shell
- **B.3** — Add `C:\msys64\mingw64\bin` to System PATH (Machine scope, NOT User) + NSSM service restart
- **B.4** — Verify in NSSM service context (`python -m weasyprint --info` ≥3 lines)
- **B.5** — Smoke test PDF generation with Italian accents (à è ì ò ù — Pasta integrale)
- **B.6** — Open the 7-day stability spike (links to `02-01-GTK3-SPIKE.md`)

### GTK3 spike artifact

`.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md` — 9-row Day-0 install matrix + 7-row continuous-logging matrix (Day 1 / Day 3 / Day 7 cadence) + verdict table + Stefano sign-off row + free-form operator notes section. 5xx <2% threshold (D-11) explicitly recorded.

### Tests

`backend/tests/unit/test_pdf_export_factory.py` — 5 unit tests:

| # | Test | Behavior verified |
|---|------|-------------------|
| 1 | `test_pdf_exporter_is_abstract` | `PdfExporter()` raises TypeError (abstractmethod enforcement) |
| 2 | `test_factory_returns_weasyprint_by_default` | `PDF_BACKEND='weasyprint'` → `WeasyPrintExporter` |
| 3 | `test_factory_returns_reportlab_when_env_says_so` | `PDF_BACKEND='reportlab'` → `ReportLabExporter` |
| 4 | `test_factory_unknown_backend_falls_through_to_weasyprint` | Unknown value falls through to `WeasyPrintExporter` (T-02-01-05) |
| 5 | `test_reportlab_smoke_renders_minimal_payload` | ReportLab path renders ≥1KB bytes starting with `%PDF` magic header |

**Lazy import verification (line numbers, post-commit `bd91e65`):**

- `from weasyprint import HTML` — `backend/app/services/pdf_export.py:74`, indented inside `async def render_shopping_list` of `WeasyPrintExporter` (not at module top).
- `grep -c "from weasyprint import HTML" backend/app/services/pdf_export.py` returns 1 (exact-count acceptance criterion).

**Test count**: 134 prior + 5 new = **139 passed** (full backend suite, no regression).

## Threat model implementation

| Threat ID | Mitigation in this commit |
|-----------|---------------------------|
| T-02-01-01 (PATH tampering) | DEPLOY.md Appendix B mandates Machine-scope PATH (NOT User) and runs as Administrator — documented verbatim |
| T-02-01-02 (info disclosure) | Spike artifact contains version numbers + verdict only — no secrets |
| T-02-01-03 (memory leak DoS) | Day 3 spike check `RSS stable over 100 PDFs` — fail → activate ReportLab |
| T-02-01-05 (env-var DoS) | Forgiving factory: `(settings.PDF_BACKEND or "weasyprint").lower()` falls through unknown values to WeasyPrint primary. Test 4 verifies. |
| T-02-01-06 (DLL load DoS) | Lazy `from weasyprint import HTML` inside method body — module imports + factory dispatch never crash even if GTK3 absent. Plan 02-05 wraps endpoint in try/except for structured 5xx envelope. |

## Deviations from Plan

### Auto-fixed issues

**1. [Rule 1 — Bug] Mypy strict mode rejected weasyprint + reportlab imports (no upstream stubs).**

- **Found during:** Task 2 type-check
- **Issue:** `app/services/pdf_export.py` failed `mypy --strict` with `import-untyped` errors for `weasyprint`, `reportlab.lib.pagesizes`, `reportlab.lib.styles`, `reportlab.platypus`, plus a `no-any-return` from `HTML(...).write_pdf()` returning `Any`.
- **Fix:** Extended `[[tool.mypy.overrides]] module` array in `backend/pyproject.toml` to include `"weasyprint.*"` and `"reportlab.*"` — follows existing `passlib.*` / `jose.*` pattern. Also annotated `pdf_bytes: bytes = HTML(...).write_pdf()` with explicit local binding to satisfy `no-any-return`.
- **Files modified:** `backend/pyproject.toml`, `backend/app/services/pdf_export.py`
- **Commit:** `bd91e65`

**2. [Rule 1 — Bug] Module docstring contained literal `from weasyprint import HTML` text, breaking the `grep -c` acceptance criterion.**

- **Found during:** Task 2 acceptance check
- **Issue:** Plan acceptance criterion `grep -c "from weasyprint import HTML" backend/app/services/pdf_export.py` must return 1, but my initial docstring also contained the literal phrase, returning 2.
- **Fix:** Reworded the docstring to "The WeasyPrint HTML import lives inside the method body" — preserves the educational note without the literal string. Resulted in exactly 1 occurrence (line 74, indented inside the method body).
- **Files modified:** `backend/app/services/pdf_export.py`
- **Commit:** `bd91e65`

**3. [Rule 1 — Bug] Two ruff E501 line-too-long warnings (line-length=100) in test file.**

- **Found during:** Task 2 ruff check
- **Issue:** Test docstring + categories dict were 101 + 109 chars.
- **Fix:** Shortened docstring to "Unknown PDF_BACKEND falls through to WeasyPrint (T-02-01-05 — never crashes startup)." and reformatted the categories dict literal across multiple lines.
- **Files modified:** `backend/tests/unit/test_pdf_export_factory.py`
- **Commit:** `bd91e65`

### Stubs / human-action gates

**HUMAN: Stefano on Windows Server 2019** — The Day 0 install matrix and 7-day continuous logging in `02-01-GTK3-SPIKE.md` cannot be filled by Claude. They require touching the production-bound NSSM service, MSYS2 install, PATH update, and live 5xx telemetry over a calendar week. The spike artifact carries an inline `[HUMAN: Stefano runs Section "Day 0 install verification" during Plan 02-03 deploy walkthrough...]` marker. This is **expected per plan** (the plan title is "GTK3 spike kit" — kit, not stability run). Plan 02-07 closure reviews the filled-in matrix before Phase 2 pause gate.

### TDD note

Plan task frontmatter declared `tdd="true"`. RED-GREEN-REFACTOR cycle observed for Task 2:

1. **RED**: created `tests/unit/test_pdf_export_factory.py` first — collection failed with `ModuleNotFoundError: No module named 'app.services.pdf_export'` (verified before implementing).
2. **GREEN**: implemented `pdf_export.py` + `PDF_BACKEND` setting + `.env.example` line — all 5 tests passed.
3. **REFACTOR**: lint + mypy + acceptance-criterion-grep tweaks (3 auto-fixes documented above).

Task 1 was scaffold-only (deps + DEPLOY.md addendum + spike checklist file) — no code-under-test, so RED-GREEN was not applicable; the verification commands listed in `<verify><automated>` ran post-edit and all passed.

## Hand-off to Plan 02-05

**Plan 02-05 (PDF endpoint, SHOP-07) imports the factory:**

```python
from app.services.pdf_export import get_pdf_exporter

@router.post("/{week_start}/export-pdf")
async def export_pdf(
    week_start: str,
    user: User = Depends(get_current_user),
    exporter: PdfExporter = Depends(get_pdf_exporter),
    session: AsyncSession = Depends(get_session),
) -> Response:
    payload = await shopping_service.build_pdf_payload(...)
    pdf_bytes = await exporter.render_shopping_list(**payload)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={...})
```

**Env consumers must set `PDF_BACKEND` in `.env.production` before Plan 02-05 ships:**

- Default value `weasyprint` is safe for development on dev box (lazy import means the module loads even without GTK3; only the endpoint fails if invoked there).
- Production value flipped to `reportlab` if the 7-day spike trips 5xx ≥2%.

## Spike status

| Field | Value |
|-------|-------|
| Spike artifact path | `.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md` |
| Spike status | **OPEN** |
| Day 0 verdict | **PENDING** (Stefano fills during Plan 02-03 deploy walkthrough) |
| Target verdict date | Day 7 from Day 0 (filled by Stefano) |
| Reviewer of verdict | Plan 02-07 closure agent |

## Self-Check: PASSED

Verifications performed (all passed):

- [x] `test -f backend/app/services/pdf_export.py` → FOUND
- [x] `test -f backend/tests/unit/test_pdf_export_factory.py` → FOUND
- [x] `test -f .planning/phases/02-differentiators/02-01-GTK3-SPIKE.md` → FOUND
- [x] `grep -E "class PdfExporter\(ABC\)|class WeasyPrintExporter|class ReportLabExporter|def get_pdf_exporter" backend/app/services/pdf_export.py` → 4 matches
- [x] `grep "PDF_BACKEND" backend/app/core/config.py` → ≥1 match with `default="weasyprint"`
- [x] `grep "PDF_BACKEND=weasyprint" backend/.env.example` → 1 match
- [x] `grep -c "Appendix B: GTK3/Pango\|mingw-w64-x86_64-pango\|nssm restart WellnessBuddyAPI" DEPLOY.md` → 5 (≥3 required)
- [x] `grep -c "GTK3 WeasyPrint 7-Day Stability Spike\|Day 0 install verification\|5xx <2%\|7-day stability checklist" 02-01-GTK3-SPIKE.md` → 5 (≥4 required)
- [x] `grep -c "from weasyprint import HTML" backend/app/services/pdf_export.py` → 1 (exact)
- [x] Lazy import line position: `pdf_export.py:74` indented inside `async def render_shopping_list` of `WeasyPrintExporter` — confirmed
- [x] `cd backend && uv sync --frozen` → succeeds (98 packages audited)
- [x] `cd backend && pytest tests/unit/test_pdf_export_factory.py -v` → 5 passed
- [x] `cd backend && pytest tests/ -q` → 139 passed (134 prior + 5 new, no regression)
- [x] `cd backend && ruff check app/services/pdf_export.py app/core/config.py tests/unit/test_pdf_export_factory.py` → All checks passed
- [x] `cd backend && mypy app/services/pdf_export.py app/core/config.py` → Success: no issues found
- [x] Commit `c5c01f2` exists in git log
- [x] Commit `bd91e65` exists in git log
