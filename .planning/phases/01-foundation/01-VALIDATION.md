---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-01
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

### Backend (Python 3.12 / FastAPI)

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio + httpx AsyncClient + pytest-postgresql |
| **Config file** | `backend/pyproject.toml` (`[tool.pytest.ini_options]`) + `backend/tests/conftest.py` |
| **Quick run command** | `cd backend && uv run pytest -x --ff -q` |
| **Full suite command** | `cd backend && uv run pytest --cov=app --cov-report=term-missing` |
| **Estimated runtime** | ~30s quick / ~90s full (Docker postgres ephemeral) |

### Frontend (Vitest + Playwright + axe-core)

| Property | Value |
|----------|-------|
| **Framework** | Vitest 1.x (unit) + Playwright 1.49 (e2e) + axe-core/playwright (a11y) |
| **Config file** | `frontend/vite.config.ts` (Vitest), `frontend/playwright.config.ts` |
| **Quick run command** | `cd frontend && pnpm vitest run --reporter=verbose` |
| **Full suite command** | `cd frontend && pnpm test:all` (vitest + playwright + axe + dark-mode-screenshot) |
| **Estimated runtime** | ~20s vitest / ~120s full (Playwright + visual diff) |

---

## Sampling Rate

- **After every task commit:** Run `pnpm vitest run` (frontend) o `uv run pytest -x` (backend) — quick affected slice
- **After every plan wave:** Run full suite per layer (`pnpm test:all` + `uv run pytest --cov`)
- **Before `/gsd:verify-work`:** Full suite must be green ON BOTH layers + axe-core + dark-mode screenshot diff
- **Max feedback latency:** 30s (quick), 120s (full)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01-monorepo | 1 | FND-01 | — | Workspaces install clean | smoke | `pnpm install && cd backend && uv sync` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01-monorepo | 1 | FND-02, MOD-09 | T-DB-01 | DB created + tz config | unit | `psql -c "SELECT current_setting('timezone')"` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02-backend-skel | 1 | FND-03 | T-API-01 | FastAPI lifespan ok | integration | `cd backend && uv run pytest tests/integration/test_app_startup.py` | ❌ W0 | ⬜ pending |
| 1-02-02 | 02-backend-skel | 1 | MOD-01..10 | T-DB-02 | Alembic baseline migration | integration | `cd backend && alembic upgrade head && pytest tests/integration/test_models.py` | ❌ W0 | ⬜ pending |
| 1-02-03 | 02-backend-skel | 1 | AI-01..04 | — | NullProvider returns 501 | unit | `cd backend && uv run pytest tests/unit/test_ai_provider.py` | ❌ W0 | ⬜ pending |
| 1-03-01 | 03-auth | 2 | AUTH-01..12 | T-AUTH-01..05 | JWT 15min + refresh rotation + family revoke + 10s grace | integration | `cd backend && uv run pytest tests/integration/test_auth.py` | ❌ W0 | ⬜ pending |
| 1-03-02 | 03-auth | 2 | AUTH-09, AUTH-10 | T-AUTH-06 | Invite token single-use + 24h expiry | integration | `cd backend && uv run pytest tests/integration/test_invite.py` | ❌ W0 | ⬜ pending |
| 1-04-01 | 04-md-parser | 2 | PLAN-01..06 | T-PARSE-01 | Tolerant normalization (BOM/CRLF/NFC/NBSP/smart-punct) | unit | `cd backend && uv run pytest tests/unit/test_normalizer.py` | ❌ W0 | ⬜ pending |
| 1-04-02 | 04-md-parser | 2 | PLAN-02, PLAN-04 | T-PARSE-02 | Evil-corpus parses without crash (Word/Notes.app/Notion/Obsidian/Notepad) | unit | `cd backend && uv run pytest tests/unit/test_parser_evil.py` | ❌ W0 | ⬜ pending |
| 1-04-03 | 04-md-parser | 2 | PLAN-06 | T-PARSE-03 | PlanParsedSchema strict validation | unit | `cd backend && uv run pytest tests/unit/test_plan_schema.py` | ❌ W0 | ⬜ pending |
| 1-04-04 | 04-md-parser | 2 | PLAN-07..10 | T-PLAN-01 | Plan upload + activate + diff API | integration | `cd backend && uv run pytest tests/integration/test_plans_api.py` | ❌ W0 | ⬜ pending |
| 1-05-01 | 05-frontend-skel | 1 | FND-04, UI-01, UI-07 | — | Vite + React 19 + Tailwind 4 @theme tokens compile clean | smoke | `cd frontend && pnpm typecheck && pnpm build` | ❌ W0 | ⬜ pending |
| 1-05-02 | 05-frontend-skel | 1 | UI-10, UI-11 | T-A11Y-01 | axe-core CI ≥4.5:1/3:1, Lighthouse a11y ≥95 | a11y | `cd frontend && pnpm test:axe` | ❌ W0 | ⬜ pending |
| 1-05-03 | 05-frontend-skel | 1 | UI-07, UI-12 | — | Dark-mode screenshot CI parity | visual | `cd frontend && pnpm test:visual` | ❌ W0 | ⬜ pending |
| 1-05-04 | 05-frontend-skel | 1 | UI-04, UI-05 | — | Motion budget tokens + prefers-reduced-motion | unit | `cd frontend && pnpm vitest run src/styles/__tests__/motion.test.ts` | ❌ W0 | ⬜ pending |
| 1-06-01 | 06-pwa-shell | 2 | FND-05, FND-06 | T-PWA-01 | Workbox NetworkFirst index.html + CacheFirst assets | smoke | `cd frontend && pnpm build && pnpm test:pwa` | ❌ W0 | ⬜ pending |
| 1-06-02 | 06-pwa-shell | 2 | FND-06 | — | Update toast + skipWaiting flow | e2e | `cd frontend && pnpm playwright test e2e/pwa-update.spec.ts` | ❌ W0 | ⬜ pending |
| 1-06-03 | 06-pwa-shell | 2 | FND-07, FND-08 | T-DEX-01 | Dexie schema + mutation_queue + persist() flow | unit | `cd frontend && pnpm vitest run src/db/__tests__/dexie.test.ts` | ❌ W0 | ⬜ pending |
| 1-06-04 | 06-pwa-shell | 2 | DEP-09 | — | PWA Lighthouse 100/100 | smoke | `cd frontend && pnpm test:lighthouse-pwa` | ❌ W0 | ⬜ pending |
| 1-07-01 | 07-features | 3 | TODAY-01..08 | T-AUTH-07, T-API-02 | /today landing renders meals + workout + weight | e2e | `cd frontend && pnpm playwright test e2e/today.spec.ts` | ❌ W0 | ⬜ pending |
| 1-07-02 | 07-features | 3 | WEIGHT-01, WEIGHT-02 | T-API-03 | Weight log API + Recharts base | integration | `cd backend && uv run pytest tests/integration/test_weight.py && cd frontend && pnpm vitest run src/components/__tests__/WeightChart.test.tsx` | ❌ W0 | ⬜ pending |
| 1-07-03 | 07-features | 3 | WORK-01, WORK-02 | T-API-03 | Workout log API + form | integration | `cd backend && uv run pytest tests/integration/test_workout.py && cd frontend && pnpm vitest run src/components/__tests__/WorkoutForm.test.tsx` | ❌ W0 | ⬜ pending |
| 1-07-04 | 07-features | 3 | AI-05..07 | T-AI-01 | AIWidget locked placeholder Italian | unit | `cd frontend && pnpm vitest run src/components/ai/__tests__/AIWidget.test.tsx` | ❌ W0 | ⬜ pending |
| 1-08-01 | 08-tone-deploy | 4 | UI-20 | — | Tone calibration mockups (3 variants 75/25 50/50 25/75) generated | manual | Stefano+Marta sign-off review | ❌ W0 | ⬜ pending |
| 1-08-02 | 08-tone-deploy | 4 | DEP-01..05, DEP-08, DEP-09 | T-DEPLOY-01 | Windows Server deploy: Uvicorn NSSM + IIS reverse proxy + win-acme cert | smoke | `curl https://wellness-buddy.epartner.it/api/health` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Tutta infrastruttura test deve essere installata in Wave 1 (plan 01 + 02 + 05) come precondizione per Wave 2+.

- [ ] `backend/pyproject.toml` — pytest + pytest-asyncio + pytest-postgresql + httpx dev deps via uv
- [ ] `backend/tests/conftest.py` — Docker postgres fixture, async client fixture, Alembic upgrade fixture
- [ ] `backend/tests/fixtures/plans/` — canonical happy-path MD + evil-corpus (Word, Notes.app, Notion, Obsidian, Notepad-BOM, NBSP)
- [ ] `frontend/package.json` — vitest + @vitest/ui + @playwright/test + @axe-core/playwright dev deps via pnpm
- [ ] `frontend/playwright.config.ts` — projects: chromium, mobile-iphone-13, dark-mode visual diff
- [ ] `frontend/vitest.config.ts` — jsdom env, setup file with theme tokens injected
- [ ] `frontend/src/test/setup.ts` — Tailwind 4 token CSS imported + axe-core matchers
- [ ] `.github/workflows/pr.yml` — lint + typecheck + test matrix (backend + frontend)
- [ ] `.github/workflows/axe-a11y.yml` — Playwright + axe-core CI gate ≥4.5:1 body / ≥3:1 large
- [ ] `.github/workflows/dark-mode-screenshot.yml` — visual diff per route light + dark

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tone calibration mockup sign-off | UI-20, ROADMAP Phase 1 exit gate | Subjective design judgment Stefano+Marta | Aprire 3 mockups (75/25, 50/50, 25/75) — focal points constanti — su iPhone reale + desktop Chrome. Selezione ratio scenario-by-scenario per UI-SPEC §8.3 |
| iPhone PWA install + offline + upgrade path | FND-05, FND-06, DEP-09 | Real-device behavior (Safari install banner, SW update toast) | Install via Safari Share → Aggiungi a Home, restart phone, open offline, verify /today renders cached, deploy new version, verify update toast |
| Resync dopo manual Dexie wipe | FND-07, FND-08 | Real-device IndexedDB eviction simulation | DevTools clear IndexedDB → reload → verify full-resync da server prima di rendering UI |
| VoiceOver smoke test | UI-13 | Screen reader real-iOS only | Settings → Accessibility → VoiceOver ON → navigate /today, /login, plan upload — verify illustrations have meaningful labels, errors role="alert" |
| Tailwind 4 + shadcn/ui v4 init verifica | FND-04 | shadcn CLI prompts interattivi non scriptable in CI | `pnpm dlx shadcn@latest init` con OKLCH override custom — verify theme.css generato matches UI-SPEC |
| WeasyPrint GTK3 spike Windows | (Phase 2 prep) | OS-level GTK runtime install | Windows Server 2019 staging: install gtk3-runtime-3.24.x-msvc.exe → Python `import weasyprint` → render test PDF |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (verified by table above — every row has automated except 1-08-01 manual + 6 in manual-only section)
- [ ] Wave 0 covers all MISSING references (test infrastructure installed in Plan 01 + 02 + 05)
- [ ] No watch-mode flags (CI runs use `vitest run` and `pytest` non-watch)
- [ ] Feedback latency < 30s (quick) / 120s (full)
- [ ] `nyquist_compliant: true` set in frontmatter (after Wave 0 completes — flag flipped by `/gsd:verify-work`)

**Approval:** pending
