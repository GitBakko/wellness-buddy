# Phase 1: Foundation - Context

**Gathered:** 2026-05-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Stack scaffolding completo + auth + models + tolerant MD parser + PWA shell + `/today` landing + weight/workout log + AI ABC stub + WIN REQUISITE UI/UX foundations (design tokens, dark mode, axe-core CI gate, Geist/Motion/sonner installed). Deploy Windows Server 2019 differito a fine Phase 1 (quando app strutturata e completa).

Esclude: weekly view + variant selector (Phase 2), shopping list (Phase 2), family sync (Phase 2), KPI dashboard (Phase 3), push notifications (Phase 3), mascot character (Phase 3), admin panel (Phase 4), AI providers concreti (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Repo Structure

- **D-01:** Monorepo pnpm workspaces — `frontend/` (React 19 + Vite 7 + TypeScript 5.6) + `backend/` (FastAPI Python 3.12). Backend NON in pnpm workspace — gestito separatamente.
- **D-02:** Python tooling: **uv** (Astral) per dependency management — lock file deterministico, install velocissimo, sostituisce pip+venv+pip-tools
- **D-03:** `.env` files: `backend/.env` + `frontend/.env.local`, entrambi in `.gitignore`. `backend/.env.example` + `frontend/.env.example` versionati con placeholder
- **D-04:** Plan MD reali Stefano+Marta vivono in **`/plans/` dir nel repo, gitignored** per privacy. `/plans/.gitkeep` + `/plans/EXAMPLE.md` (sintetico) versionati. CI test corpus usa fixture sintetici in `backend/tests/fixtures/plans/` (versionati, non sensibili)

### Domain & Deploy

- **D-05:** Dominio produzione: **`wellness-buddy.epartner.it`** — sottodominio esistente epartner.it, win-acme cert flow noto
- **D-06:** First deploy strategy: **deferred a fine Phase 1, quando app strutturata e completa**. Sviluppo locale-first con Docker Compose (postgres + uvicorn + vite dev server). Deploy single-shot solo dopo login + auth + plan upload + /today + weight/workout log tutti funzionanti localmente
- **D-07:** Test deploy intermedio in staging Windows VM (interno NXTLink) opzionale dopo auth+models, NON obbligatorio

### CI/CD

- **D-08:** **GitHub Actions** per CI — runners hosted ubuntu-latest per backend/frontend lint+test+build, runners windows-latest opzionale per integration test deploy (post-Phase 1)
- **D-09:** Pipelines Sprint 1: `pr.yml` (lint + type-check + unit test + build), `axe-a11y.yml` (Playwright + axe-core su frontend dist), `dark-mode-screenshot.yml` (Playwright visual diff dark/light). Pre-commit hook locale via Husky + lint-staged
- **D-10:** Deploy CI/CD setup deferred: NO automated deploy Sprint 1 — manual deploy quando app pronta. CI deploy automation deferred Sprint 4

### Testing Strategy

- **D-11:** Backend: **pytest + pytest-asyncio + httpx AsyncClient + pytest-postgresql** (Docker postgres tmp container per integration test isolato). Coverage gate ≥80% per `services/`, `parsers/`, `auth/`
- **D-12:** Frontend: **Vitest** (unit + component) + **Playwright** (e2e) + **axe-core/playwright** (a11y CI gate ≥4.5:1 body / ≥3:1 large/icons) + **vitest visual snapshots** (dark mode parity)
- **D-13:** Test DB: Docker postgres ephemeral per CI, dev locale usa stesso container Docker Compose. Mai sqlite (divergenza JSONB/TIMESTAMPTZ)
- **D-14:** Plan parser test corpus evil-input: Word `.docx`-export, Notes.app, Notion, Obsidian, Notepad, BOM/CRLF/NFC/NBSP/smart quotes — fixture in `backend/tests/fixtures/plans/evil/`

### Auth & Onboarding Flow

- **D-15:** First-login UX: dopo successful login, mostra full-screen welcome con CTA "Abilita storage offline" che chiama `navigator.storage.persist()` — granular timing migliora grant rate vs auto-prompt at app boot
- **D-16:** PWA install prompt: NO auto-prompt. Banner sottile "Installa Wellness Buddy" mostrato dopo 2nd visit (storia in localStorage). iOS Safari: bottom sheet con illustrazione che indica share button + "Aggiungi a Home" (UI-SPEC §10)
- **D-17:** Token invito flow: admin genera link `/register?token=XXX` via `POST /api/auth/invite`. User clicca link → form registrazione pre-compilato con token → submit → account + login automatico

### Error Handling & Resilience

- **D-18:** Error boundaries: **global ErrorBoundary** + **per-route Suspense fallback** per offline-mode awareness. Errori catturati loggati a backend `/api/errors` (sprint 1 simple endpoint, no sentry)
- **D-19:** Offline error UX: toast italiano "Modalità offline — modifiche salvate, sync al ritorno online" via Dexie mutation queue. Banner persistente top quando offline >30s
- **D-20:** API errors response sempre JSON `{detail: string, code: string}`. Frontend traduce `code` → italian copy locale via `copy.it.ts`

### Observability

- **D-21:** Backend logging: **structlog** con JSON output. Log levels: DEBUG dev, INFO production. Request ID via FastAPI middleware per traceability
- **D-22:** Frontend observability: **NESSUNA Sprint 1**. Sentry/Plausible deferred Sprint 4 per non gonfiare bundle e perché 2 utenti famiglia in Phase 1
- **D-23:** Audit log Sprint 1 minimo: `Group`/`User`/`NutritionPlan` create/update/delete loggati a `audit_log` table (Phase 4 espande)

### Secrets

- **D-24:** `SECRET_KEY` generato via `python -c "import secrets; print(secrets.token_hex(32))"` — diverso per dev/staging/prod. Mai versionato
- **D-25:** Database password generato `openssl rand -base64 32`, persistito in `backend/.env` produzione (Windows DPAPI cifrato + ACL su file)
- **D-26:** VAPID keys generate Phase 3 quando push attivato — Sprint 1 NO VAPID
- **D-27:** No rotation policy automatica Sprint 1. Manual rotation procedure documentata in DEPLOY.md

### Database

- **D-28:** Database `WellnessBuddy` creato manualmente prima primo `alembic upgrade head` via `psql -U postgres -c "CREATE DATABASE WellnessBuddy;"`. Documented in DEPLOY.md
- **D-29:** Connection pool: `pool_size=15, max_overflow=10` (per research SUMMARY.md). Re-evaluate Phase 4 con k6 load test
- **D-30:** Alembic migration baseline (`0000_baseline.py`) genera schema completo Sprint 1: User+Group+NutritionPlan+WeeklyPlanVariant+WorkoutLog+WeightLog+ShoppingListState+InviteToken+AuditLog. Group+visibility entities create anche se family sync arriva Phase 2

### AI Layer Stub

- **D-31:** `AIProvider` ABC in `backend/app/ai/base.py` con metodi async stub. `NullProvider` in `backend/app/ai/null_provider.py` ritorna 501 con messaggio italiano "AI non disponibile"
- **D-32:** Provider DI: factory `get_ai_provider()` in `backend/app/ai/factory.py`, registrato a lifespan startup come `app.state.ai_provider`. Endpoint `Depends(get_ai_provider)` Phase 1 returna 501
- **D-33:** Frontend AIWidget: componente disabilitato in `frontend/src/components/ai/AIWidget.tsx` con placeholder UI "AI non disponibile — coming soon" (illustrazione + Italian copy). Architettura SSE/WebSocket predisposta ma non attiva

### Claude's Discretion

- Esatti name/path SQLAlchemy model files (lib/models/X.py vs models/X.py)
- Esatto wiring Alembic env.py + script.py.mako boilerplate
- Esatto folder structure FastAPI (api/ vs routers/, services/ vs business/)
- Workbox config dettagliato (caching strategy per ogni asset type secondo UI-SPEC §10 + research)
- Dexie schema versioning + upgrade hooks pattern
- shadcn/ui components da installare via CLI (button, input, card, dialog, sheet, sonner, etc — UI-SPEC §14 lista 17)
- Lottie animations specifiche Sprint 1 (welcome screen + meal-completion celebration ≤800ms)
- Storyset/Open Doodles illustration scelta finale per empty states + login hero

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project foundation

- `.planning/PROJECT.md` — Win Requisite UI/UX, core value, key decisions, constraints
- `.planning/REQUIREMENTS.md` — REQ-IDs Phase 1 (FND-* AUTH-* MOD-* PLAN-* TODAY-* WEIGHT-01/02 WORK-01/02 AI-01..07 DEP-01..05/08/09 + UI-01..20 cross-cutting)
- `.planning/ROADMAP.md` §Phase 1 — Goal, success criteria, hard dependency locks, pause gate
- `.planning/STATE.md` — Current focus pointer

### Research

- `.planning/research/SUMMARY.md` — Stack picks, architecture pillars, top-5 pitfalls, WIN REQUISITE UI/UX strategy, Sprint 1 must-haves
- `.planning/research/STACK.md` — Versioni puntuali, Tailwind 4 deviation, WeasyPrint vs ReportLab decision, UI/UX library stack
- `.planning/research/ARCHITECTURE.md` — 3-tier offline-first, state split, AI provider DI sketch, multi-user Group model, auth refresh rotation, SW strategy
- `.planning/research/PITFALLS.md` — iOS PWA storage eviction, SW stale index.html, JWT refresh race, MD parser brittleness, WIN REQUISITE traps, mitigations + phase mapping
- `.planning/research/FEATURES.md` — Table stakes Phase 1 features, anti-features list, engagement patterns, notification budget

### Design contract (locked Phase 1)

- `.planning/phase-01-foundation/01-UI-SPEC.md` — **APPROVED 6/6 dimensions**. Design tokens (Tailwind 4 @theme), 4-size typography scale + escape hatch, OKLCH palette light/dark, Italian copy lock, motion budget, accessibility gates, focal points per surface, exit gate (tone calibration mockups Stefano+Marta)

### Project root

- `CLAUDE.md` — Conventions code + UI/UX 1-14, architecture summary, build order locks
- `docs/PROMPT_CONTRACT_WELLNESS_BUDDY.md` v1.0 — Original product contract (27/04/2026), API endpoints list, model spec, sprint plan

### External (no docs in repo)

No external specs/ADRs beyond above — requirements fully captured in `.planning/` artifacts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **None** — greenfield project, no existing code in `d:/Develop/AI/WellnessBuddy/` apart `docs/PROMPT_CONTRACT_WELLNESS_BUDDY.md` and `.planning/` artifacts

### Established Patterns (from NXTLink ecosystem, recommended for adoption)

- **FastAPI structure** (per ARCHITECTURE.md): `app/api/` routes, `app/core/` config+auth+deps, `app/models/` SQLAlchemy, `app/schemas/` Pydantic, `app/services/` business logic, `app/parsers/` MD parser, `app/ai/` provider abstraction
- **React structure**: `src/components/`, `src/pages/`, `src/stores/` (Zustand), `src/hooks/`, `src/services/` (API client), `src/ai/` (AI client stub), `src/i18n/copy.it.ts` (Italian-only Sprint 1)
- **Auth pattern**: JWT access in memory + refresh HttpOnly cookie + rotation + 10s grace (per ARCHITECTURE.md §Auth)
- **Error response format**: `{detail: string, code: string}` standard NXTLink

### Integration Points

- **PostgreSQL existente** in produzione Windows Server 2019 — solo `CREATE DATABASE WellnessBuddy;` necessario, no install
- **win-acme** già configurato per altri sottodomini epartner.it — flow SSL noto a Stefano
- **NSSM Windows service** pattern noto da MANTIS/ePartner deploy
- **IIS reverse proxy** noto setup `/api/* → localhost:8000`, `/* → dist/`

</code_context>

<specifics>
## Specific Ideas

- "Aspetto a metà tra eleganza/minimal e giocoso/friendly. Senza questo il progetto è fallito" — citato verbatim da PROJECT.md, anchor design decisions cross-phase
- "Vedo cosa devo mangiare oggi e segno il peso" — Core Value minimo, ogni feature Phase 1 deve servire questo
- "Scene-by-scene tilt": routine = 70/30 elegant; celebrations = 30/70 playful (UI-SPEC §8.3)
- Mascot character SEED Phase 3: water-droplet o scale-spirit, **NON** trope avocado
- Stefano familiare con: win-acme, NSSM, IIS, ReportLab (anche se pick è WeasyPrint con ReportLab fallback)
- 2 utenti reali: Stefano + Marta — pasti serali condivisi (cene+pranzi default `group_shared` Phase 2)

</specifics>

<deferred>
## Deferred Ideas

- WebSocket vs SSE vs polling decisione finale per `condiviso` badge → Phase 2 research
- WeasyPrint GTK3 spike Windows Server → Phase 2
- VAPID keys + push notifications → Phase 3
- Mascot character design final + Lottie+Rive integration → Phase 3
- PostgreSQL Row-Level Security defense-in-depth → Phase 4
- k6 load test connection pool sizing → Phase 4
- Vite 7 → 8 upgrade decision → Phase 4 retrospective
- Sentry/Plausible frontend observability → Phase 4
- Automated deploy CI/CD pipeline → Phase 4
- Concrete AI providers (Ollama, OpenAI, Anthropic) → Phase 5
- AI cost caps + prompt-injection adversarial corpus → Phase 5
- Recharts performance optimization se dataset grandi → Phase 3+
- i18n refactor a `react-i18next` → v2 (post-Sprint 5) se utenti non-italiani

### Reviewed Todos (not folded)

None — no prior todos to fold.

</deferred>

---
*Phase: 01-foundation*
*Context gathered: 2026-05-01*
