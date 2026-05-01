---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-01
revised: 2026-05-01
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Revised after checker feedback: Plan 02 split into 02a + 02b, Plan 05 split into 05a + 05b, waves recomputed per `wave = max(deps) + 1`.

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
| **Config file** | `frontend/vitest.config.ts` + `frontend/playwright.config.ts` |
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
| 1-01-01 | 01-monorepo | W1 | FND-01 | — | Workspaces install clean | smoke | `pnpm install && cd backend && uv sync` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01-monorepo | W1 | FND-02, MOD-09 | T-DB-01 | DB created + tz config | unit | `psql -c "SELECT current_setting('timezone')"` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01-monorepo | W1 | FND-09 | — | CI workflows + Husky | smoke | `test -f .github/workflows/pr.yml && test -f .husky/pre-commit` | ❌ W0 | ⬜ pending |
| 1-02a-01 | 02a-backend-core | W2 | FND-03 | T-API-01 | FastAPI lifespan stub + main.py + core scaffolding | integration | `cd backend && uv run pytest tests/integration/test_app_startup.py tests/integration/test_health.py` | ❌ W0 | ⬜ pending |
| 1-02a-02 | 02a-backend-core | W2 | MOD-01..10 | T-DB-02 | All 10 models + Alembic baseline + audit_service | integration | `cd backend && uv run alembic upgrade head && uv run pytest tests/unit/test_models.py tests/integration/test_alembic_baseline.py` | ❌ W0 | ⬜ pending |
| 1-02b-01 | 02b-ai-stubs | W2 | AI-01..04, AI-07 | T-AI-01 | AI ABC + NullProvider + factory + lifespan extension + stub routers | integration | `cd backend && uv run python -c "from app.main import app"` | ❌ W0 | ⬜ pending |
| 1-02b-02 | 02b-ai-stubs | W2 | AI-04, AUTH-12 | T-AI-01 | AI endpoints + stub envelope tests + provider unit tests | integration+unit | `cd backend && uv run pytest tests/unit/test_ai_provider.py tests/integration/test_ai_api.py tests/integration/test_stub_endpoints.py` | ❌ W0 | ⬜ pending |
| 1-05a-01 | 05a-frontend-build | W2 | FND-04, UI-01, UI-03, UI-07 | T-XSS-01 | Vite + Tailwind 4 @theme + shadcn 17 primitives + ESLint hex ban | smoke | `cd frontend && pnpm typecheck && pnpm build && pnpm lint --max-warnings=0` | ❌ W0 | ⬜ pending |
| 1-05a-02 | 05a-frontend-build | W2 | FND-04 | — | App shell skeleton (main.tsx + router) + 4 PWA icons + version.json | smoke | `cd frontend && pnpm build && test -f public/icons/icon-192.png` | ❌ W0 | ⬜ pending |
| 1-05b-01 | 05b-frontend-behavior | W2 | FND-09, UI-18 | — | copy.it.ts + format.ts + hooks + Zustand stores | smoke | `cd frontend && pnpm typecheck && grep -q 'Buongiorno' src/i18n/copy.it.ts && grep -q "Intl.NumberFormat" src/lib/format.ts` | ❌ W0 | ⬜ pending |
| 1-05b-02 | 05b-frontend-behavior | W2 | UI-04, UI-05, UI-10, UI-11, UI-12 | T-A11Y-01, T-MOTION-01 | Vitest + Playwright + axe + visual diff + Lighthouse + motion test | a11y+visual | `cd frontend && pnpm vitest run src/styles/__tests__/motion.test.ts && pnpm exec playwright install --with-deps chromium` | ❌ W0 | ⬜ pending |
| 1-03-01 | 03-auth | W3 | AUTH-01..12 | T-AUTH-01..05 | JWT 15min + refresh rotation + family revoke + 10s grace | integration | `cd backend && uv run pytest tests/integration/test_auth.py` | ❌ W0 | ⬜ pending |
| 1-03-02 | 03-auth | W3 | AUTH-09, AUTH-10, FND-08, D-15 | T-AUTH-06 | Frontend auth + persistStorage.ts (export check) + invite | unit+e2e | `cd frontend && pnpm vitest run src/tests/unit/refreshTokenAtomic.test.ts src/tests/unit/auth.test.ts` | ❌ W0 | ⬜ pending |
| 1-06-01 | 06-pwa-shell | W3 | FND-05, FND-06 | T-PWA-01 | Workbox NetworkFirst index.html + CacheFirst assets + Dexie schema | smoke+unit | `cd frontend && pnpm vitest run src/db/__tests__/dexie.test.ts && pnpm build` | ❌ W0 | ⬜ pending |
| 1-06-02 | 06-pwa-shell | W3 | FND-06, D-26 | — | Update toast + skipWaiting + AppShell + No VAPID assertion | e2e | `cd frontend && pnpm playwright test e2e/pwa-update.spec.ts e2e/pwa-install.spec.ts` | ❌ W0 | ⬜ pending |
| 1-04-01 | 04-md-parser | W4 | PLAN-01..06 | T-PARSE-01..03 | Tolerant normalization + evil-corpus + strict Pydantic schema | unit | `cd backend && uv run pytest tests/unit/test_normalizer.py tests/unit/test_parser_evil.py tests/unit/test_plan_schema.py` | ❌ W0 | ⬜ pending |
| 1-04-02 | 04-md-parser | W4 | PLAN-07..10 | T-PLAN-01 | Plan upload + activate + diff API | integration | `cd backend && uv run pytest tests/integration/test_plans_api.py` | ❌ W0 | ⬜ pending |
| 1-04-03 | 04-md-parser | W4 | PLAN-08, PLAN-09 | — | Frontend Plans page + dropzone + diff view | unit+e2e | `cd frontend && pnpm vitest run src/components/plans/__tests__/` | ❌ W0 | ⬜ pending |
| 1-07-01 | 07-features | W5 | TODAY-01..08 | T-API-02 | /today landing renders meals + workout + weight | e2e | `cd frontend && pnpm playwright test e2e/today.spec.ts` | ❌ W0 | ⬜ pending |
| 1-07-02 | 07-features | W5 | WEIGHT-01, WEIGHT-02 | T-API-03 | Weight log API + Recharts | integration | `cd backend && uv run pytest tests/integration/test_weight.py && cd frontend && pnpm vitest run src/components/__tests__/WeightChart.test.tsx` | ❌ W0 | ⬜ pending |
| 1-07-03 | 07-features | W5 | WORK-01, WORK-02 | T-API-03 | Workout log API + form | integration | `cd backend && uv run pytest tests/integration/test_workout.py && cd frontend && pnpm vitest run src/components/__tests__/WorkoutForm.test.tsx` | ❌ W0 | ⬜ pending |
| 1-07-04 | 07-features | W5 | AI-05..07 | T-AI-01 | AIWidget locked placeholder Italian | unit | `cd frontend && pnpm vitest run src/components/ai/__tests__/AIWidget.test.tsx` | ❌ W0 | ⬜ pending |
| 1-08-01 | 08-tone-deploy | W6 | UI-20 | — | Tone calibration mockups (3 variants 75/25 50/50 25/75) generated | manual | Stefano+Marta sign-off review | ❌ W0 | ⬜ pending |
| 1-08-02 | 08-tone-deploy | W6 | DEP-01..05, DEP-08, DEP-09 | T-DEPLOY-01 | Windows Server deploy: Uvicorn NSSM + IIS reverse proxy + win-acme cert | smoke | `curl https://wellness-buddy.epartner.it/api/health` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Tutta infrastruttura test deve essere installata in Wave 1 (plan 01) + Wave 2 (plans 02a/02b, 05a/05b) come precondizione per Wave 3+.

- [ ] `backend/pyproject.toml` — pytest + pytest-asyncio + pytest-postgresql + httpx dev deps via uv (Plan 01)
- [ ] `backend/tests/conftest.py` — Docker postgres fixture, async client fixture, Alembic upgrade fixture (Plan 02a)
- [ ] `backend/tests/fixtures/plans/` — canonical happy-path MD + evil-corpus (Plan 04)
- [ ] `frontend/package.json` — vitest + @vitest/ui + @playwright/test + @axe-core/playwright dev deps via pnpm (Plan 01 manifest, Plan 05b actually installs)
- [ ] `frontend/playwright.config.ts` — projects: chromium, mobile-iphone-13, dark-mode visual diff (Plan 05b)
- [ ] `frontend/vitest.config.ts` — jsdom env, setup file with theme tokens injected (Plan 05b)
- [ ] `frontend/src/test/setup.ts` — Tailwind 4 token CSS imported + axe-core matchers (Plan 05b)
- [ ] `.github/workflows/pr.yml` — lint + typecheck + test matrix (backend + frontend) (Plan 01)
- [ ] `.github/workflows/axe-a11y.yml` — Playwright + axe-core CI gate ≥4.5:1 body / ≥3:1 large (Plan 01)
- [ ] `.github/workflows/dark-mode-screenshot.yml` — visual diff per route light + dark (Plan 01)

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
| TIMESTAMPTZ DB probe via psql | MOD-09 | Optional manual DB inspection (CI now uses unit test test_users_created_at_is_timestamptz) | `psql -d WellnessBuddy -c "SELECT data_type FROM information_schema.columns WHERE table_name='users' AND column_name='created_at'"` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (verified by table above — every row has automated except 1-08-01 manual + 7 in manual-only section)
- [ ] Wave 0 covers all MISSING references (test infrastructure installed in Plan 01 + 02a/02b + 05a/05b)
- [ ] No watch-mode flags (CI runs use `vitest run` and `pytest` non-watch)
- [ ] Feedback latency < 30s (quick) / 120s (full)
- [ ] `nyquist_compliant: true` set in frontmatter (after Wave 0 completes — flag flipped by `/gsd:verify-work`)

**Approval:** pending
