# Phase 1: Foundation - Research

**Researched:** 2026-05-01
**Domain:** Greenfield monorepo PWA â€” React 19 + FastAPI + PostgreSQL, offline-first, multi-user, AI-pluggable, Italian-only
**Confidence:** HIGH

## Summary

Phase 1 lays foundations that every later phase inherits without retrofit. Stack and architecture are pre-locked by upstream research (`STACK.md`, `ARCHITECTURE.md`) and CONTEXT.md (33 user decisions). Research role here is **prescriptive specification** â€” concrete file structures, exact CLI commands, exact code snippets, library version pins re-confirmed, CI/CD configs, and Phase 1-specific pitfall preventions â€” so the planner can decompose into 5-8 plans without re-investigating.

The phase divides into 8 natural plan units: (1) Monorepo + tooling scaffolding, (2) Backend skeleton + DB + Alembic baseline, (3) Auth + JWT refresh rotation + invite tokens, (4) MD parser + plan upload/activate/diff, (5) Frontend skeleton + Tailwind 4 @theme + shadcn/ui + UI tokens + axe-core CI, (6) PWA shell + Dexie + mutation queue + version polling + persistence, (7) /today landing + weight + workout + AI placeholder, (8) Tone calibration mockups + Stefano+Marta exit gate review. Deploy to Windows Server 2019 happens at end-of-phase only when all 7 plans land green.

**Primary recommendation:** Execute the 8 plans in dependency order with 3 parallelizable Wave 1 streams (backend skeleton â€– frontend skeleton â€– tone mockup), then converge into auth + parser + features + PWA + deploy. WIN REQUISITE foundations (Tailwind 4 @theme tokens, axe-core CI gate â‰¥95, dark-mode CI screenshots, Italian copy lock, motion budget enforced) MUST land in Plan 5 (Frontend Skeleton) before any feature plan touches UI â€” otherwise hardcoded hex/font-sizes proliferate and retrofit is expensive.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Repo Structure:**
- **D-01:** Monorepo pnpm workspaces â€” `frontend/` (React 19 + Vite 7 + TypeScript 5.6) + `backend/` (FastAPI Python 3.12). Backend NON in pnpm workspace â€” gestito separatamente.
- **D-02:** Python tooling: **uv** (Astral) per dependency management â€” lock file deterministico, install velocissimo, sostituisce pip+venv+pip-tools
- **D-03:** `.env` files: `backend/.env` + `frontend/.env.local`, entrambi in `.gitignore`. `backend/.env.example` + `frontend/.env.example` versionati con placeholder
- **D-04:** Plan MD reali Stefano+Marta vivono in **`/plans/` dir nel repo, gitignored** per privacy. `/plans/.gitkeep` + `/plans/EXAMPLE.md` (sintetico) versionati. CI test corpus usa fixture sintetici in `backend/tests/fixtures/plans/` (versionati, non sensibili)

**Domain & Deploy:**
- **D-05:** Dominio produzione: **`wellness-buddy.epartner.it`**
- **D-06:** First deploy strategy: **deferred a fine Phase 1**. Sviluppo locale-first con Docker Compose
- **D-07:** Test deploy intermedio in staging Windows VM opzionale, NON obbligatorio

**CI/CD:**
- **D-08:** **GitHub Actions** runners ubuntu-latest per backend/frontend lint+test+build
- **D-09:** Pipelines Sprint 1: `pr.yml`, `axe-a11y.yml`, `dark-mode-screenshot.yml`. Husky + lint-staged pre-commit
- **D-10:** Deploy CI/CD setup deferred Sprint 4 â€” manual deploy Sprint 1

**Testing Strategy:**
- **D-11:** Backend: **pytest + pytest-asyncio + httpx AsyncClient + pytest-postgresql**. Coverage â‰¥80% per `services/`, `parsers/`, `auth/`
- **D-12:** Frontend: **Vitest + Playwright + axe-core/playwright + vitest visual snapshots**
- **D-13:** Test DB: Docker postgres ephemeral. Mai sqlite
- **D-14:** Plan parser test corpus evil-input in `backend/tests/fixtures/plans/evil/`

**Auth & Onboarding Flow:**
- **D-15:** First-login UX: full-screen welcome con CTA "Abilita storage offline" â†’ `navigator.storage.persist()`
- **D-16:** PWA install prompt: NO auto-prompt. Banner sottile dopo 2nd visit. iOS Safari bottom sheet illustrato
- **D-17:** Token invito flow: admin â†’ `POST /api/auth/invite` â†’ `/register?token=XXX`

**Error Handling & Resilience:**
- **D-18:** Global ErrorBoundary + per-route Suspense fallback. Errors â†’ backend `/api/errors`
- **D-19:** Offline UX: toast italiano + banner persistente >30s offline
- **D-20:** API errors sempre JSON `{detail: string, code: string}`. Frontend traduce via `copy.it.ts`

**Observability:**
- **D-21:** Backend logging: **structlog** JSON. Request ID middleware
- **D-22:** Frontend observability: NESSUNA Sprint 1
- **D-23:** Audit log Sprint 1 minimo: Group/User/NutritionPlan CRUD

**Secrets:**
- **D-24:** `SECRET_KEY` via `python -c "import secrets; print(secrets.token_hex(32))"`, mai versionato
- **D-25:** Database password `openssl rand -base64 32`, `.env` produzione DPAPI cifrato
- **D-26:** VAPID keys Phase 3
- **D-27:** No rotation policy automatica Sprint 1

**Database:**
- **D-28:** Database `WellnessBuddy` creato manualmente via `psql -U postgres -c "CREATE DATABASE WellnessBuddy;"`
- **D-29:** Connection pool: `pool_size=15, max_overflow=10`
- **D-30:** Alembic baseline `0000_baseline.py` schema completo Sprint 1

**AI Layer Stub:**
- **D-31:** `AIProvider` ABC in `backend/app/ai/base.py`. `NullProvider` returns 501 "AI non disponibile"
- **D-32:** Provider DI: factory `get_ai_provider()`, lifespan startup, `app.state.ai_provider`
- **D-33:** Frontend `AIWidget` placeholder UI "AI non disponibile â€” coming soon"

### Claude's Discretion

- Esatti name/path SQLAlchemy model files
- Esatto wiring Alembic env.py + script.py.mako
- Esatto folder structure FastAPI (api/ vs routers/, services/ vs business/)
- Workbox config dettagliato per ogni asset type
- Dexie schema versioning + upgrade hooks pattern
- shadcn/ui components da installare via CLI (UI-SPEC Â§6 17 components)
- Lottie animations Sprint 1 (welcome screen + meal-completion â‰¤800ms)
- Storyset/Open Doodles illustration scelta finale empty states + login hero

### Deferred Ideas (OUT OF SCOPE)

- WebSocket vs SSE vs polling decisione finale `condiviso` badge â†’ Phase 2
- WeasyPrint GTK3 spike Windows Server â†’ Phase 2
- VAPID keys + push notifications â†’ Phase 3
- Mascot character design final + Lottie+Rive integration â†’ Phase 3
- PostgreSQL Row-Level Security â†’ Phase 4
- k6 load test connection pool sizing â†’ Phase 4
- Vite 7 â†’ 8 upgrade decision â†’ Phase 4
- Sentry/Plausible frontend observability â†’ Phase 4
- Automated deploy CI/CD pipeline â†’ Phase 4
- Concrete AI providers â†’ Phase 5
- AI cost caps + prompt-injection corpus â†’ Phase 5
- Recharts performance optimization â†’ Phase 3+
- i18n refactor a `react-i18next` â†’ v2

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FND-01 | Monorepo pnpm workspaces frontend+backend con linter | Â§Standard Stack + Â§Monorepo Layout â€” exact pnpm-workspace.yaml + ESLint flat + ruff/mypy configs |
| FND-02 | Database PostgreSQL `WellnessBuddy` + Alembic init baseline | Â§Database â€” `CREATE DATABASE` + Alembic env.py async config + `0000_baseline.py` |
| FND-03 | Backend FastAPI skeleton + SQLAlchemy 2 async + asyncpg pool 15/10 + lifespan | Â§Backend File Structure + Â§Models Â§Code Examples â€” `main.py` lifespan + `core/database.py` |
| FND-04 | Frontend Vite + React 19 + Tailwind 4 @theme + shadcn/ui CLI + Geist + lucide + sonner + Motion v12 | Â§Frontend File Structure + Â§Tailwind 4 Theme + Â§shadcn/ui Install Order |
| FND-05 | PWA shell vite-plugin-pwa + manifest + SW NetworkFirst index + CacheFirst hashed | Â§PWA Workbox Config + UI-SPEC Â§10.4 manifest |
| FND-06 | Update flow `/version.json` polling + toast skipWaiting | Â§Workbox Update Flow + UI-SPEC Â§10.2 toast copy |
| FND-07 | Dexie schema cache_* + mutation_queue + drafts UUIDs server | Â§Dexie Schema with Versioning |
| FND-08 | `navigator.storage.persist()` flow first-login + Dexie-empty-but-JWT-valid resync | Â§Persistent Storage Flow |
| FND-09 | Italian copy.it.ts struttura | Â§Italian copy.it.ts + UI-SPEC Â§7.2 (~80 strings) |
| AUTH-01 â€” AUTH-12 | Login/logout/refresh/JWT/invite tokens/auth errors | Â§Auth Concrete Implementation Â§JWT Refresh Â§Invite Flow |
| MOD-01 â€” MOD-10 | Models User/Group/NutritionPlan/WeeklyPlanVariant/WorkoutLog/WeightLog/ShoppingListState/InviteToken/AuditLog + indexes + TIMESTAMPTZ + IANA tz | Â§SQLAlchemy 2 Models + Â§Alembic Baseline |
| PLAN-01 â€” PLAN-10 | MD parser tollerante + Pydantic strict + upload + activate + diff + assign | Â§MD Parser Concrete + Â§Plans API |
| TODAY-01 â€” TODAY-08 | `/today` landing + meal completion + workout + weight + status indicator + offline | Â§Today View + Â§Components UI-SPEC Â§6.4 |
| WEIGHT-01, WEIGHT-02 | Grafico Recharts + storico tabellare | Â§Weight + Recharts pattern |
| WORK-01, WORK-02 | Form workout + storico filtrabile | Â§Workout |
| AI-01 â€” AI-07 | AI ABC + NullProvider + DI + endpoints 501 + Frontend locked widget + WebSocket predisposto + .env config | Â§AI Provider DI Sketch |
| DEP-01 â€” DEP-05, DEP-08, DEP-09 | NSSM + IIS reverse proxy + win-acme + .env + Docker Compose + DEPLOY.md | Â§Deployment Architecture + Â§Docker Compose Dev |
| UI-01 â€” UI-20 | WIN REQUISITE: tokens + mobile-first + shadcn customizzato + motion + dark mode + axe-core + Lighthouse + dark-mode CI + VoiceOver + illustrations + form errors + iOS keyboard + tone + Italian formatting + emoji budget + impeccable | Â§Tailwind 4 Theme + Â§axe-core CI + Â§Motion Budget + Â§Tone Calibration |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| User authentication (login/logout) | API / Backend | Browser (Zustand auth-in-mem + HttpOnly cookie) | Token issuance + rotation server-only; client holds access token in memory |
| Refresh token rotation + family revocation | API / Backend | Database (refresh_tokens table) | Server is sole authority on token validity; family tracking requires DB |
| MD plan parsing + validation | API / Backend | â€” | Tolerant parser + strict Pydantic v2 validation must be reusable from CLI; never client-side |
| Plan storage + active flag | Database | API | Canonical truth lives in PostgreSQL; partial unique index `WHERE is_active = true` |
| Daily meal completion state | API / Backend | Browser (Dexie cache + mutation queue) | Server canonical; Dexie mirror for offline writes |
| Weight logging + chart | API / Backend | Browser (Dexie cache, Recharts render) | Server stores points; Recharts renders client-side from cache |
| Workout logging | API / Backend | Browser (Dexie cache + mutation queue) | Same offline-first pattern as weight |
| App shell (PWA install + offline) | Browser / Service Worker | CDN/IIS Static (immutable hashed assets) | NetworkFirst index.html + CacheFirst /assets/* |
| `/version.json` polling | Browser | API / Backend (serves `{version, build_hash}`) | Backend generates at build, frontend polls every 5min |
| `navigator.storage.persist()` request | Browser | â€” | Pure client API; cannot be granted server-side |
| Italian localization | Browser (copy.it.ts) | â€” | All UI strings client-side; backend errors send `code` only, frontend translates |
| AI provider stub (NullProvider 501) | API / Backend | Browser (locked AIWidget placeholder) | Backend factory + DI; frontend shows placeholder UI |
| Audit log | API / Backend | Database | Mutations logged on write paths; retrieval Phase 4 |
| Dark mode | Browser (CSS @media + ThemeToggle in Zustand) | â€” | Pure client concern; PWA manifest theme-color via media queries |
| axe-core a11y CI gate | CI / GitHub Actions | Browser (Playwright runtime) | Playwright runs in CI against built dist/; blocks PR merge |
| Dark-mode screenshot tests | CI / GitHub Actions | Browser (Playwright runtime) | Visual diff in CI; blocks PR if regression |

## Standard Stack

### Core (versions verified vs STACK.md 2026-05-01)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | `^19.2.5` | UI framework | Current stable; React 19 use/server actions/ref-as-prop. [VERIFIED: STACK.md] |
| Vite | `^7.0` | Build tool | Stable, plugin ecosystem mature. Vite 8 deferred Phase 4. [VERIFIED: STACK.md] |
| TailwindCSS | `^4.0` | CSS engine + design tokens | Oxide engine 2-5x faster, container queries, `@theme` first-class. [VERIFIED: STACK.md] |
| TypeScript | `^5.6` | Type safety | Standard, Zod inference, RHF + shadcn integration. [VERIFIED: STACK.md] |
| Python | `3.12.x` | Runtime | FastAPI 0.130+ requires 3.10+; 3.12 best perf. [VERIFIED: STACK.md] |
| FastAPI | `^0.136.1` | Web framework | Async-native, Pydantic v2, OpenAPI auto. [VERIFIED: STACK.md] |
| SQLAlchemy | `^2.0` | ORM | 2.0 async API canonical 2026 pattern. [VERIFIED: STACK.md] |
| Pydantic | `^2.7` | Validation | Required by FastAPI 0.136. [VERIFIED: STACK.md] |
| asyncpg | `^0.29` | PostgreSQL async driver | Required for SQLAlchemy 2.0 async. [VERIFIED: STACK.md] |
| Alembic | `^1.13` | DB migrations | Standard. Contract mandates Alembic-only. [VERIFIED: STACK.md] |
| Uvicorn | `^0.30` | ASGI server | Standard FastAPI server, NSSM-wrappable. [VERIFIED: STACK.md] |
| python-jose[cryptography] | `^3.3` | JWT | Standard JWT lib. [VERIFIED: STACK.md] |
| passlib[bcrypt] | `^1.7` | Password hashing | rounds=12 minimum. [VERIFIED: STACK.md] |
| python-multipart | `^0.0.9` | File upload | `.md` upload endpoint. [VERIFIED: STACK.md] |

### Supporting Frontend

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Zustand | `^5.0` | Client state | UI state, auth-in-mem token, theme. [VERIFIED: STACK.md] |
| @tanstack/react-query | `^5.x` | Server state | All API caching, optimistic mutations. [VERIFIED: STACK.md] |
| @tanstack/query-sync-storage-persister | latest | Persist Query cache | Cache survives reload â€” Phase 1 stretch, Phase 2 hard requirement. [CITED: tanstack docs] |
| dexie | `^4.4` | IndexedDB wrapper | Cache + mutation queue + drafts. [VERIFIED: STACK.md] |
| react-router | `^7.x` | Routing | v7 unified data router. [VERIFIED: STACK.md] |
| vite-plugin-pwa | `^0.21` | PWA manifest + SW | Workbox 7 zero-config. [VERIFIED: STACK.md] |
| workbox-window | `^7.x` | SW lifecycle | SW comm from page. [VERIFIED: STACK.md] |
| motion | `^12.x` | Component animation | Hybrid native/JS, spring physics. Use `motion/react`. [VERIFIED: STACK.md] |
| lucide-react | `^0.460+` | Icons | 1600 stroke icons, tree-shakable, friendly. [VERIFIED: STACK.md] |
| geist | latest | Geist Sans + Mono fonts | npm-installable variable fonts. [VERIFIED: STACK.md] |
| @vercel/style-guide or font-loader | â€” | Instrument Serif (escape hatch) | UI-SPEC Â§3.2 â€” `/today` greeting only, max 1 per page |
| sonner | `^1.7` | Toasts | 47M weekly, beautiful default. [VERIFIED: STACK.md] |
| react-hook-form | `^7.53` | Form state | Min re-renders, shadcn/ui native. [VERIFIED: STACK.md] |
| zod | `^3.23` | Schema validation | Type-safe, share with backend Pydantic shape. [VERIFIED: STACK.md] |
| @hookform/resolvers | `^3.9` | RHF + Zod bridge | `zodResolver(schema)`. [VERIFIED: STACK.md] |
| recharts | `^3.0` | Charts | SVG, Tailwind-themeable, declarative JSX. [VERIFIED: STACK.md] |
| date-fns | `^4.x` | Dates | Tree-shakable, IANA tz support. [VERIFIED: STACK.md] |
| react-day-picker | `^9.x` | Calendar | Headless, WCAG 2.1 AA, shadcn-wrappable. [VERIFIED: STACK.md] |
| react-markdown | `^9.x` | Plan preview render | Safe, customizable. [VERIFIED: STACK.md] |
| remark-gfm | `^4.x` | GFM plugin | Tables in plan diff. [VERIFIED: STACK.md] |
| class-variance-authority | `^0.7` | Variant API | Standard shadcn. [VERIFIED: STACK.md] |
| tailwind-merge | `^2.x` | Class conflict resolution | `cn()` utility. [VERIFIED: STACK.md] |
| clsx | `^2.x` | Conditional classes | shadcn standard. [VERIFIED: STACK.md] |
| tailwindcss-animate | `^1.x` | Animation utilities | shadcn keyframes. [VERIFIED: STACK.md] |

### Supporting Backend

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| structlog | `^24.x` | JSON structured logging | D-21 â€” Request ID middleware [CITED: structlog docs] |
| python-markdown | `^3.7` | MD AST | Used by parser. [VERIFIED: STACK.md] |
| python-dotenv | `^1.0` | `.env` loading | Standard. [VERIFIED: STACK.md] |
| httpx | `^0.27` | Async HTTP | Phase 5 AI providers; not used Phase 1. [VERIFIED: STACK.md] |
| pytest | `^8.x` | Test runner | D-11 [VERIFIED: STACK.md] |
| pytest-asyncio | `^0.24` | Async test | D-11 [VERIFIED: STACK.md] |
| pytest-postgresql | `^6.x` | Docker postgres tmp container | D-11/D-13 [CITED: pypi pytest-postgresql] |
| ruff | `^0.6` | Lint + format | 100x flake8 [VERIFIED: STACK.md] |
| mypy | `^1.x` | Type check | Strict on `app/` |

### Dev Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| Vitest `^2.x` | Frontend unit + component | Built-in Vite ecosystem |
| Playwright `^1.x` | E2E + axe-core integration | Test PWA + a11y |
| @axe-core/playwright | latest | a11y CI gate â‰¥4.5:1 / â‰¥3:1 |
| ESLint `^9` (flat config) | Lint | `eslint-plugin-react`, `eslint-plugin-react-hooks` |
| Prettier `^3` | Format | + `prettier-plugin-tailwindcss` |
| Husky `^9` | Git hooks | pre-commit lint-staged |
| lint-staged `^15` | Staged lint | Husky companion |
| uv | Python deps | Astral, deterministic lock |
| Docker Compose | Dev postgres | D-08 / D-13 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pnpm workspaces | Turborepo | Turborepo adds caching only with multiple JS packages. Single frontend â†’ overhead Phase 1. Re-evaluate Phase 4. |
| Tailwind 4 | Tailwind 3 | v3 = no `@theme`, no Oxide, no first-class container queries. Materially worse for WIN REQUISITE. |
| Vite 7 | Vite 8 | v8 stable but Rolldown plugin ecosystem still settling. Hold v7. |
| ReportLab | WeasyPrint (Phase 2) | WeasyPrint = HTML+CSS reuse Tailwind tokens. Phase 1 doesn't ship PDF â€” decision deferred Phase 2 GTK3 spike. |
| Geist | Inter | Inter = neutral SaaS. Geist = friendlier apertures, slightly rounder, maps to elegant+playful brief. |
| date-fns v4 | Day.js / Temporal | Day.js smaller but less TZ. Temporal needs polyfill. date-fns v4 = best 2026 baseline. |
| Lucide | Phosphor | Lucide 16x dominant 2026, default in shadcn/ui. |
| Sonner | react-hot-toast | Sonner 9.7x lead, shadcn default. |
| FastAPI | Django/Flask | FastAPI = async-first + OpenAPI + Pydantic. Standard 2026 choice for this stack. |
| pnpm | npm/yarn | pnpm = symlink store, faster, workspaces first-class. |

**Frontend Installation:**

```bash
cd frontend
pnpm create vite@latest . --template react-ts

# Core React + state
pnpm add react@^19.2 react-dom@^19.2 react-router@^7
pnpm add zustand@^5 @tanstack/react-query@^5 @tanstack/query-sync-storage-persister
pnpm add dexie@^4.4

# UI / Design system
pnpm add -D tailwindcss@^4 @tailwindcss/vite postcss autoprefixer
pnpm add class-variance-authority clsx tailwind-merge tailwindcss-animate
pnpm add lucide-react geist
pnpm add @radix-ui/react-dialog @radix-ui/react-dropdown-menu \
  @radix-ui/react-popover @radix-ui/react-tabs @radix-ui/react-toggle \
  @radix-ui/react-toast @radix-ui/react-select @radix-ui/react-checkbox \
  @radix-ui/react-radio-group @radix-ui/react-switch @radix-ui/react-label

# Animation
pnpm add motion

# Forms + validation
pnpm add react-hook-form zod @hookform/resolvers

# Toast
pnpm add sonner

# Charts + dates
pnpm add recharts@^3 date-fns@^4 react-day-picker@^9

# Markdown render
pnpm add react-markdown remark-gfm

# PWA
pnpm add -D vite-plugin-pwa workbox-window

# Dev tooling
pnpm add -D vitest @testing-library/react @testing-library/jest-dom \
  @testing-library/user-event jsdom \
  @playwright/test @axe-core/playwright \
  prettier prettier-plugin-tailwindcss \
  eslint @eslint/js typescript-eslint eslint-plugin-react eslint-plugin-react-hooks
pnpm add -D husky lint-staged

# shadcn/ui CLI init (after Tailwind 4 @theme set up)
pnpm dlx shadcn@latest init
```

**Backend Installation (uv-managed):**

```bash
cd backend
uv init --python 3.12
uv add "fastapi[standard]>=0.136"
uv add "uvicorn[standard]>=0.30"
uv add "sqlalchemy[asyncio]>=2.0" asyncpg alembic
uv add "pydantic>=2.7" "pydantic-settings>=2.0"
uv add "python-jose[cryptography]>=3.3" "passlib[bcrypt]>=1.7"
uv add python-multipart python-dotenv
uv add markdown
uv add structlog
uv add --dev pytest pytest-asyncio pytest-postgresql httpx ruff mypy
```

**Version verification (run before locking pyproject/package.json):**

```bash
# Frontend
pnpm view react version
pnpm view vite version
pnpm view tailwindcss version
pnpm view @tanstack/react-query version
pnpm view dexie version
pnpm view motion version
pnpm view sonner version

# Backend
uv pip index versions fastapi
uv pip index versions sqlalchemy
uv pip index versions pydantic
```

Versions in `STACK.md` were verified 2026-05-01. If any version drift detected during planning, re-verify and update CONTEXT.md.

## Architecture Patterns

### System Architecture Diagram

```
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  iPhone / Android / Desktop Browser              â”‚
                    â”‚                                                   â”‚
   user input  â”€â†’   â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”‚
                    â”‚  â”‚ React 19 UI     â”‚    â”‚ Service Worker   â”‚     â”‚
                    â”‚  â”‚ (Vite 7 build)  â”‚    â”‚ (vite-plugin-pwa)â”‚     â”‚
                    â”‚  â”‚ Tailwind 4 CSS  â”‚    â”‚ Workbox 7 SW     â”‚     â”‚
                    â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚
                    â”‚           â”‚                       â”‚              â”‚
                    â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”     â”‚
                    â”‚  â”‚ Zustand stores  â”‚    â”‚ NetworkFirst     â”‚     â”‚
                    â”‚  â”‚ (auth/ui/theme) â”‚    â”‚ /index.html      â”‚     â”‚
                    â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚ CacheFirst       â”‚     â”‚
                    â”‚           â”‚             â”‚ /assets/*-hash.* â”‚     â”‚
                    â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚
                    â”‚  â”‚ TanStack Query  â”‚              â”‚              â”‚
                    â”‚  â”‚ (server cache,  â”‚              â”‚              â”‚
                    â”‚  â”‚ optimistic mut) â”‚              â”‚              â”‚
                    â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â”‚              â”‚
                    â”‚           â”‚                       â”‚              â”‚
                    â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”              â”‚              â”‚
                    â”‚  â”‚ Dexie.js v4.4   â”‚              â”‚              â”‚
                    â”‚  â”‚ â–¸ cache_*       â”‚              â”‚              â”‚
                    â”‚  â”‚ â–¸ mutation_q    â”‚              â”‚              â”‚
                    â”‚  â”‚ â–¸ drafts        â”‚              â”‚              â”‚
                    â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â”‚              â”‚
                    â”‚           â”‚                       â”‚              â”‚
                    â”‚           â”‚ /version.json poll    â”‚              â”‚
                    â”‚           â”‚ skipWaiting+toast     â”‚              â”‚
                    â”‚           â”‚                       â”‚              â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚                       â”‚
                  HTTPS (JWT Bearer in header,          â”‚
                  refresh in HttpOnly cookie scoped     â”‚
                  /api/auth)                            â”‚
                                â”‚                       â”‚
   Phase 1 dev:                 â–¼                       â–¼
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â”‚  Phase 1 dev: Vite dev server (5173) â†â†’ Uvicorn (8000)      â”‚
   â”‚     (proxy /api â†’ 8000, /* â†’ vite)                          â”‚
   â”‚                                                              â”‚
   â”‚  End of Phase 1 deploy: IIS reverse proxy                   â”‚
   â”‚     /api/* â†’ 127.0.0.1:8000 (Uvicorn via NSSM)              â”‚
   â”‚     /*     â†’ frontend/dist/ (static)                        â”‚
   â”‚     SSL terminated at IIS (win-acme cert)                   â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                â”‚
                                â–¼
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â”‚  FastAPI 0.136 (Python 3.12, uv-managed)                    â”‚
   â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚
   â”‚  â”‚ api/   â”‚â†’ â”‚ services/â”‚â†’ â”‚ models/  â”‚  â”‚ ai/        â”‚    â”‚
   â”‚  â”‚ routes â”‚  â”‚ biz logicâ”‚  â”‚ SQLAlch  â”‚  â”‚ ABC + Null â”‚    â”‚
   â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚
   â”‚      â”‚            â”‚             â”‚              â”‚           â”‚
   â”‚  â”Œâ”€â”€â”€â–¼â”€â”€â”€â”    â”Œâ”€â”€â”€â–¼â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”     â”‚
   â”‚  â”‚ core/ â”‚    â”‚parsersâ”‚    â”‚ schemas/â”‚  â”‚ NullProvider     â”‚
   â”‚  â”‚ auth+ â”‚    â”‚ MDâ†’   â”‚    â”‚ Pydanticâ”‚  â”‚ â†’ 501 Italianâ”‚   â”‚
   â”‚  â”‚ DI +  â”‚    â”‚ JSON  â”‚    â”‚ v2 strict  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
   â”‚  â”‚ configâ”‚    â”‚ tolerant   â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                  â”‚
   â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”˜                                     â”‚
   â”‚      â”‚                                                      â”‚
   â”‚  â”Œâ”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                              â”‚
   â”‚  â”‚ Lifespan startup:          â”‚                              â”‚
   â”‚  â”‚ â–¸ build_provider() â†’ state â”‚                              â”‚
   â”‚  â”‚ â–¸ engine + sessionmaker    â”‚                              â”‚
   â”‚  â”‚ â–¸ structlog config         â”‚                              â”‚
   â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                              â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                â”‚
                â”‚ asyncpg pool 15/10
                â”‚
                â–¼
   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
   â”‚  PostgreSQL â€” DATABASE: WellnessBuddy (canonical truth)     â”‚
   â”‚  â–¸ TIMESTAMPTZ everywhere (UTC storage)                     â”‚
   â”‚  â–¸ IANA tz on User                                          â”‚
   â”‚  â–¸ Group + visibility enum (Phase 1 schema, Phase 2 use)    â”‚
   â”‚  â–¸ Indexes: (user_id, week_start), (user_id, date), etc.    â”‚
   â”‚  â–¸ refresh_tokens table for rotation + family revocation    â”‚
   â”‚  â–¸ audit_log table (Phase 1 minimal)                        â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Recommended Project Structure

```
wellness-buddy/                      # monorepo root
â”œâ”€â”€ package.json                     # pnpm workspace root (frontend only)
â”œâ”€â”€ pnpm-workspace.yaml              # workspaces: ['frontend']
â”œâ”€â”€ pnpm-lock.yaml                   # versioned
â”œâ”€â”€ docker-compose.yml               # dev postgres
â”œâ”€â”€ .gitignore                       # backend/.env, frontend/.env.local, /plans/, dist/, .venv/
â”œâ”€â”€ .gitattributes                   # text=auto eol=lf, *.md text eol=lf
â”œâ”€â”€ README.md                        # project overview + dev setup
â”œâ”€â”€ CLAUDE.md                        # already exists
â”œâ”€â”€ DEPLOY.md                        # Windows Server 2019 deploy guide (Phase 1 end)
â”œâ”€â”€ .github/
â”‚   â””â”€â”€ workflows/
â”‚       â”œâ”€â”€ pr.yml                   # lint + type-check + unit + build
â”‚       â”œâ”€â”€ axe-a11y.yml             # Playwright + axe-core
â”‚       â””â”€â”€ dark-mode-screenshot.yml # Playwright visual diff
â”œâ”€â”€ .husky/
â”‚   â””â”€â”€ pre-commit                   # lint-staged
â”œâ”€â”€ plans/                           # MD plans Stefano+Marta â€” gitignored
â”‚   â”œâ”€â”€ .gitkeep                     # versioned
â”‚   â””â”€â”€ EXAMPLE.md                   # synthetic, versioned
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ package.json                 # frontend deps
â”‚   â”œâ”€â”€ pnpm-lock.yaml -> ../        # via workspace
â”‚   â”œâ”€â”€ vite.config.ts               # vite-plugin-pwa registered
â”‚   â”œâ”€â”€ tsconfig.json
â”‚   â”œâ”€â”€ eslint.config.js             # flat config
â”‚   â”œâ”€â”€ .prettierrc.cjs              # + prettier-plugin-tailwindcss
â”‚   â”œâ”€â”€ components.json              # shadcn/ui CLI config
â”‚   â”œâ”€â”€ playwright.config.ts         # axe + visual snapshots
â”‚   â”œâ”€â”€ vitest.config.ts
â”‚   â”œâ”€â”€ .env.example                 # versioned, placeholder
â”‚   â”œâ”€â”€ .env.local                   # gitignored
â”‚   â”œâ”€â”€ public/
â”‚   â”‚   â”œâ”€â”€ icons/
â”‚   â”‚   â”‚   â”œâ”€â”€ icon-192.png
â”‚   â”‚   â”‚   â”œâ”€â”€ icon-512.png
â”‚   â”‚   â”‚   â”œâ”€â”€ icon-maskable-512.png
â”‚   â”‚   â”‚   â””â”€â”€ apple-touch-icon-180.png
â”‚   â”‚   â”œâ”€â”€ illustrations/           # Storyset SVGs colorized via tokens
â”‚   â”‚   â”‚   â”œâ”€â”€ empty-today.svg
â”‚   â”‚   â”‚   â”œâ”€â”€ empty-plan.svg
â”‚   â”‚   â”‚   â”œâ”€â”€ login-hero.svg
â”‚   â”‚   â”‚   â””â”€â”€ error-fallback.svg
â”‚   â”‚   â””â”€â”€ version.json             # generated at build, {version, build_hash}
â”‚   â”œâ”€â”€ index.html                   # manifest link, theme-color media queries
â”‚   â””â”€â”€ src/
â”‚       â”œâ”€â”€ main.tsx                 # entry, registers SW via virtual:pwa-register/react
â”‚       â”œâ”€â”€ App.tsx                  # router shell, ErrorBoundary wrap
â”‚       â”œâ”€â”€ router.tsx               # react-router v7 createBrowserRouter
â”‚       â”œâ”€â”€ pages/
â”‚       â”‚   â”œâ”€â”€ Login.tsx
â”‚       â”‚   â”œâ”€â”€ InviteSignup.tsx
â”‚       â”‚   â”œâ”€â”€ Today.tsx            # /today landing
â”‚       â”‚   â”œâ”€â”€ Plans.tsx            # plan upload + diff
â”‚       â”‚   â”œâ”€â”€ History.tsx          # weight + workout history
â”‚       â”‚   â””â”€â”€ Settings.tsx
â”‚       â”œâ”€â”€ components/
â”‚       â”‚   â”œâ”€â”€ ui/                  # shadcn/ui customized primitives
â”‚       â”‚   â”‚   â”œâ”€â”€ button.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ input.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ textarea.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ label.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ checkbox.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ switch.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ select.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ radio-group.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ dialog.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ sheet.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ dropdown-menu.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ form.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ card.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ tabs.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ calendar.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ sonner.tsx
â”‚       â”‚   â”‚   â””â”€â”€ skeleton.tsx
â”‚       â”‚   â”œâ”€â”€ layout/
â”‚       â”‚   â”‚   â”œâ”€â”€ AppShell.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ AppBar.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ BottomTabBar.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ NavigationRail.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ ErrorBoundary.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ SyncStatusPip.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ UpdatePromptToast.tsx
â”‚       â”‚   â”‚   â””â”€â”€ IOSInstallBanner.tsx
â”‚       â”‚   â”œâ”€â”€ today/
â”‚       â”‚   â”‚   â”œâ”€â”€ MealCard.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ MacroDisplay.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ DayStatusIndicator.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ WeightQuickLog.tsx
â”‚       â”‚   â”‚   â””â”€â”€ WorkoutForm.tsx
â”‚       â”‚   â”œâ”€â”€ plans/
â”‚       â”‚   â”‚   â”œâ”€â”€ PlanUploadDropzone.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ PlanDiffView.tsx
â”‚       â”‚   â”‚   â””â”€â”€ PlanPreviewMd.tsx
â”‚       â”‚   â”œâ”€â”€ weight/
â”‚       â”‚   â”‚   â”œâ”€â”€ WeightChart.tsx
â”‚       â”‚   â”‚   â””â”€â”€ WeightHistoryTable.tsx
â”‚       â”‚   â”œâ”€â”€ workout/
â”‚       â”‚   â”‚   â””â”€â”€ WorkoutHistoryTable.tsx
â”‚       â”‚   â”œâ”€â”€ auth/
â”‚       â”‚   â”‚   â”œâ”€â”€ LoginForm.tsx
â”‚       â”‚   â”‚   â”œâ”€â”€ InviteSignupForm.tsx
â”‚       â”‚   â”‚   â””â”€â”€ PersistStorageWelcome.tsx   # full-screen welcome D-15
â”‚       â”‚   â””â”€â”€ ai/
â”‚       â”‚       â””â”€â”€ AIWidget.tsx     # locked placeholder
â”‚       â”œâ”€â”€ stores/                  # Zustand
â”‚       â”‚   â”œâ”€â”€ auth.ts              # access token in-mem
â”‚       â”‚   â”œâ”€â”€ theme.ts             # light/dark/system
â”‚       â”‚   â”œâ”€â”€ ui.ts                # current week, modal state
â”‚       â”‚   â””â”€â”€ sync.ts              # online/offline, pending count
â”‚       â”œâ”€â”€ services/                # TanStack Query hooks + API client
â”‚       â”‚   â”œâ”€â”€ api.ts               # fetch wrapper, JWT injection, refresh interceptor
â”‚       â”‚   â”œâ”€â”€ auth.ts              # login/logout/refresh/me/invite
â”‚       â”‚   â”œâ”€â”€ plans.ts             # upload/list/activate/diff
â”‚       â”‚   â”œâ”€â”€ today.ts             # /today data
â”‚       â”‚   â”œâ”€â”€ weekly.ts            # /api/weekly (Phase 2 stub Phase 1)
â”‚       â”‚   â”œâ”€â”€ workout.ts           # log/list
â”‚       â”‚   â”œâ”€â”€ weight.ts            # log/list
â”‚       â”‚   â””â”€â”€ version.ts           # /version.json polling
â”‚       â”œâ”€â”€ lib/
â”‚       â”‚   â”œâ”€â”€ refreshTokenAtomic.ts # singleton refresh promise
â”‚       â”‚   â”œâ”€â”€ mutationQueue.ts     # Dexie outbox helpers
â”‚       â”‚   â”œâ”€â”€ persistStorage.ts    # navigator.storage.persist() flow
â”‚       â”‚   â”œâ”€â”€ queryClient.ts       # TanStack QueryClient + Dexie persister
â”‚       â”‚   â”œâ”€â”€ cn.ts                # clsx + tailwind-merge
â”‚       â”‚   â””â”€â”€ format.ts            # Intl.NumberFormat('it-IT'), Intl.Collator('it')
â”‚       â”œâ”€â”€ db/
â”‚       â”‚   â”œâ”€â”€ dexie.ts             # Dexie schema definition
â”‚       â”‚   â”œâ”€â”€ schema.ts            # TypeScript table types
â”‚       â”‚   â””â”€â”€ migrations.ts        # version().upgrade() hooks
â”‚       â”œâ”€â”€ hooks/
â”‚       â”‚   â”œâ”€â”€ useOnline.ts
â”‚       â”‚   â”œâ”€â”€ useReducedMotion.ts  # wraps motion useReducedMotion
â”‚       â”‚   â”œâ”€â”€ useMediaQuery.ts
â”‚       â”‚   â””â”€â”€ useTheme.ts
â”‚       â”œâ”€â”€ i18n/
â”‚       â”‚   â””â”€â”€ copy.it.ts           # ~80 strings UI-SPEC Â§7.2
â”‚       â”œâ”€â”€ styles/
â”‚       â”‚   â”œâ”€â”€ theme.css            # Tailwind 4 @theme block
â”‚       â”‚   â””â”€â”€ globals.css          # base resets + utilities
â”‚       â””â”€â”€ tests/
â”‚           â”œâ”€â”€ e2e/                 # Playwright
â”‚           â”‚   â”œâ”€â”€ auth.spec.ts
â”‚           â”‚   â”œâ”€â”€ pwa.spec.ts
â”‚           â”‚   â”œâ”€â”€ today.spec.ts
â”‚           â”‚   â””â”€â”€ a11y.spec.ts
â”‚           â”œâ”€â”€ visual/              # dark-mode screenshot diff
â”‚           â”‚   â””â”€â”€ routes.spec.ts
â”‚           â””â”€â”€ unit/                # Vitest
â”‚               â”œâ”€â”€ components/
â”‚               â””â”€â”€ lib/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ pyproject.toml               # uv-managed, ruff/mypy/pytest config
â”‚   â”œâ”€â”€ uv.lock
â”‚   â”œâ”€â”€ .python-version              # 3.12
â”‚   â”œâ”€â”€ .env.example                 # versioned
â”‚   â”œâ”€â”€ .env                         # gitignored
â”‚   â”œâ”€â”€ alembic.ini
â”‚   â”œâ”€â”€ alembic/
â”‚   â”‚   â”œâ”€â”€ env.py                   # async config
â”‚   â”‚   â”œâ”€â”€ script.py.mako
â”‚   â”‚   â””â”€â”€ versions/
â”‚   â”‚       â””â”€â”€ 0000_baseline.py     # full Phase 1 schema
â”‚   â””â”€â”€ app/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ main.py                  # FastAPI app factory + lifespan
â”‚       â”œâ”€â”€ core/
â”‚       â”‚   â”œâ”€â”€ __init__.py
â”‚       â”‚   â”œâ”€â”€ config.py            # Pydantic settings BaseSettings
â”‚       â”‚   â”œâ”€â”€ security.py          # JWT encode/decode, password hash
â”‚       â”‚   â”œâ”€â”€ database.py          # async engine + sessionmaker
â”‚       â”‚   â”œâ”€â”€ deps.py              # get_current_user, get_session, get_ai_provider
â”‚       â”‚   â”œâ”€â”€ exceptions.py        # custom exception â†’ HTTP error mapping
â”‚       â”‚   â”œâ”€â”€ logging.py           # structlog config
â”‚       â”‚   â””â”€â”€ middleware.py        # request ID, idempotent grace window
â”‚       â”œâ”€â”€ models/
â”‚       â”‚   â”œâ”€â”€ __init__.py
â”‚       â”‚   â”œâ”€â”€ base.py              # Base, common columns (TIMESTAMPTZ created_at)
â”‚       â”‚   â”œâ”€â”€ user.py
â”‚       â”‚   â”œâ”€â”€ group.py
â”‚       â”‚   â”œâ”€â”€ plan.py              # NutritionPlan
â”‚       â”‚   â”œâ”€â”€ variant.py           # WeeklyPlanVariant
â”‚       â”‚   â”œâ”€â”€ workout.py           # WorkoutLog
â”‚       â”‚   â”œâ”€â”€ weight.py            # WeightLog
â”‚       â”‚   â”œâ”€â”€ shopping.py          # ShoppingListState
â”‚       â”‚   â”œâ”€â”€ invite.py            # InviteToken
â”‚       â”‚   â”œâ”€â”€ refresh.py           # RefreshToken (rotation + family)
â”‚       â”‚   â””â”€â”€ audit.py             # AuditLog
â”‚       â”œâ”€â”€ schemas/
â”‚       â”‚   â”œâ”€â”€ __init__.py
â”‚       â”‚   â”œâ”€â”€ auth.py              # LoginRequest, RefreshResponse, etc.
â”‚       â”‚   â”œâ”€â”€ plan.py              # PlanCreate, PlanResponse
â”‚       â”‚   â”œâ”€â”€ plan_parsed.py       # PlanParsedSchema strict (parser output)
â”‚       â”‚   â”œâ”€â”€ today.py             # TodayResponse aggregate
â”‚       â”‚   â”œâ”€â”€ workout.py
â”‚       â”‚   â”œâ”€â”€ weight.py
â”‚       â”‚   â”œâ”€â”€ invite.py
â”‚       â”‚   â””â”€â”€ ai.py                # AIRequest/Response shapes (501 stub)
â”‚       â”œâ”€â”€ api/
â”‚       â”‚   â”œâ”€â”€ __init__.py
â”‚       â”‚   â”œâ”€â”€ deps.py              # local auth deps re-export
â”‚       â”‚   â”œâ”€â”€ auth.py              # /api/auth/*
â”‚       â”‚   â”œâ”€â”€ plans.py             # /api/plans/*
â”‚       â”‚   â”œâ”€â”€ today.py             # /api/today
â”‚       â”‚   â”œâ”€â”€ weekly.py            # /api/weekly/* (stub Phase 1)
â”‚       â”‚   â”œâ”€â”€ workout.py
â”‚       â”‚   â”œâ”€â”€ weight.py
â”‚       â”‚   â”œâ”€â”€ shopping.py          # stub Phase 2
â”‚       â”‚   â”œâ”€â”€ ai.py                # /api/ai/* all 501
â”‚       â”‚   â”œâ”€â”€ admin.py             # invite gen, plan assign
â”‚       â”‚   â”œâ”€â”€ errors.py            # /api/errors (frontend error log)
â”‚       â”‚   â””â”€â”€ version.py           # /version.json (also static)
â”‚       â”œâ”€â”€ services/
â”‚       â”‚   â”œâ”€â”€ __init__.py
â”‚       â”‚   â”œâ”€â”€ auth_service.py      # token issue/rotate/revoke
â”‚       â”‚   â”œâ”€â”€ plan_service.py      # upload, activate, diff
â”‚       â”‚   â”œâ”€â”€ today_service.py     # aggregate today's data
â”‚       â”‚   â”œâ”€â”€ workout_service.py
â”‚       â”‚   â”œâ”€â”€ weight_service.py
â”‚       â”‚   â””â”€â”€ audit_service.py
â”‚       â”œâ”€â”€ parsers/
â”‚       â”‚   â”œâ”€â”€ __init__.py
â”‚       â”‚   â”œâ”€â”€ normalizer.py        # BOM/CRLF/NFC/NBSP/smart-punct pipeline
â”‚       â”‚   â”œâ”€â”€ plan_parser.py       # tolerant section parser
â”‚       â”‚   â””â”€â”€ plan_sections.py     # individual section parsers
â”‚       â”œâ”€â”€ ai/
â”‚       â”‚   â”œâ”€â”€ __init__.py
â”‚       â”‚   â”œâ”€â”€ base.py              # AIProvider ABC
â”‚       â”‚   â”œâ”€â”€ null_provider.py     # NullProvider (501 Italian)
â”‚       â”‚   â””â”€â”€ factory.py           # build_provider() reads AI_PROVIDER env
â”‚       â””â”€â”€ tests/
â”‚           â”œâ”€â”€ __init__.py
â”‚           â”œâ”€â”€ conftest.py          # pytest-postgresql fixture, async client
â”‚           â”œâ”€â”€ fixtures/
â”‚           â”‚   â””â”€â”€ plans/
â”‚           â”‚       â”œâ”€â”€ valid/
â”‚           â”‚       â”‚   â”œâ”€â”€ stefano_synthetic.md
â”‚           â”‚       â”‚   â””â”€â”€ marta_synthetic.md
â”‚           â”‚       â””â”€â”€ evil/        # corpus
â”‚           â”‚           â”œâ”€â”€ word_export.md         # CRLF + smart quotes
â”‚           â”‚           â”œâ”€â”€ notes_app.md           # NFD decomposed
â”‚           â”‚           â”œâ”€â”€ notion_export.md       # emoji headings
â”‚           â”‚           â”œâ”€â”€ obsidian_export.md
â”‚           â”‚           â”œâ”€â”€ notepad_bom.md         # UTF-8 BOM
â”‚           â”‚           â””â”€â”€ nbsp_in_headings.md
â”‚           â”œâ”€â”€ unit/
â”‚           â”‚   â”œâ”€â”€ test_normalizer.py
â”‚           â”‚   â”œâ”€â”€ test_plan_parser.py
â”‚           â”‚   â”œâ”€â”€ test_plan_parsed_schema.py
â”‚           â”‚   â”œâ”€â”€ test_security.py             # JWT encode/decode/rotate
â”‚           â”‚   â””â”€â”€ test_models.py
â”‚           â””â”€â”€ integration/
â”‚               â”œâ”€â”€ test_auth_api.py
â”‚               â”œâ”€â”€ test_plans_api.py
â”‚               â”œâ”€â”€ test_today_api.py
â”‚               â”œâ”€â”€ test_weight_api.py
â”‚               â”œâ”€â”€ test_workout_api.py
â”‚               â””â”€â”€ test_ai_api.py               # 501 stub
â””â”€â”€ deploy/                          # ops scripts (Phase 1 end)
    â”œâ”€â”€ nssm/
    â”‚   â””â”€â”€ install-service.ps1
    â”œâ”€â”€ iis/
    â”‚   â””â”€â”€ web.config               # reverse proxy
    â””â”€â”€ win-acme/
        â””â”€â”€ README.md
```

### Pattern 1: Tailwind 4 `@theme` Token Block (UI-01, UI-07)

**What:** Single CSS file (`frontend/src/styles/theme.css`) declaring all design tokens via `@theme` directive. Components reference via `var(--token-name)` or `theme(...)` Tailwind utility â€” never hardcoded hex/font-size/radius.

**When to use:** Always. Imported in `main.tsx` before any other CSS.

**Example (concrete tokens locked from UI-SPEC Â§2-5, Â§12):**

```css
/* frontend/src/styles/theme.css */
/* Source: UI-SPEC Â§12 Final Lock List + Â§2 spacing + Â§3 typography + Â§4 colors + Â§5 motion */
@import "tailwindcss";

@theme {
  /* â”€â”€â”€â”€â”€ Spacing â”€â”€â”€â”€â”€ */
  --spacing-0: 0;
  --spacing-px: 1px;
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
  --spacing-16: 64px;
  --spacing-20: 80px;

  /* â”€â”€â”€â”€â”€ Radius â”€â”€â”€â”€â”€ */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-button: 12px;
  --radius-card: 16px;
  --radius-sheet: 20px;
  --radius-pill: 9999px;

  /* â”€â”€â”€â”€â”€ Font families â”€â”€â”€â”€â”€ */
  --font-sans: "Geist Sans", system-ui, sans-serif;
  --font-mono: "Geist Mono", ui-monospace, monospace;
  --font-display: "Instrument Serif", "Geist Sans", serif;

  /* â”€â”€â”€â”€â”€ Type scale (4 base + 1 escape hatch) â”€â”€â”€â”€â”€ */
  --text-caption: 0.75rem;        /* 12px */
  --text-base: 1rem;              /* 16px */
  --text-heading: 1.375rem;       /* 22px */
  --text-display: 1.75rem;        /* 28px */
  --text-display-serif: 2.25rem;  /* 36px â€” /today greeting only */

  --leading-tight: 1.1;
  --leading-display: 1.2;
  --leading-heading: 1.25;
  --leading-caption: 1.4;
  --leading-base: 1.5;

  /* â”€â”€â”€â”€â”€ Colors (light) â”€â”€â”€â”€â”€ */
  --color-bg: oklch(98.5% 0.005 80);
  --color-bg-elev: oklch(100% 0 0);
  --color-surface: oklch(99% 0.005 80);
  --color-surface-muted: oklch(96.5% 0.008 80);

  --color-neutral-50:  oklch(98% 0.005 80);
  --color-neutral-100: oklch(95% 0.006 80);
  --color-neutral-200: oklch(90% 0.008 80);
  --color-neutral-300: oklch(83% 0.010 80);
  --color-neutral-400: oklch(70% 0.012 80);
  --color-neutral-500: oklch(58% 0.014 80);
  --color-neutral-600: oklch(48% 0.014 80);
  --color-neutral-700: oklch(38% 0.012 80);
  --color-neutral-800: oklch(28% 0.010 80);
  --color-neutral-900: oklch(20% 0.008 80);
  --color-neutral-950: oklch(13% 0.006 80);

  --color-coral-50:  oklch(97% 0.020 30);
  --color-coral-100: oklch(93% 0.045 28);
  --color-coral-200: oklch(86% 0.080 28);
  --color-coral-300: oklch(78% 0.115 28);
  --color-coral-400: oklch(70% 0.145 28);
  --color-coral-500: oklch(63% 0.165 28);
  --color-coral-600: oklch(55% 0.165 28);
  --color-coral-700: oklch(46% 0.150 28);
  --color-coral-800: oklch(36% 0.115 28);
  --color-coral-900: oklch(28% 0.085 28);

  --color-leaf-50:  oklch(97% 0.025 145);
  --color-leaf-500: oklch(60% 0.135 145);
  --color-leaf-700: oklch(42% 0.115 145);

  --color-success: oklch(58% 0.130 145);
  --color-success-bg: oklch(96% 0.030 145);
  --color-warning: oklch(72% 0.140 75);
  --color-warning-bg: oklch(96% 0.045 80);
  --color-destructive: oklch(56% 0.190 25);
  --color-destructive-bg: oklch(95% 0.035 25);

  --color-focus-ring: oklch(45% 0.030 250);
  --focus-ring-width: 2px;
  --focus-ring-offset: 2px;

  --color-text: var(--color-neutral-800);
  --color-text-muted: var(--color-neutral-500);
  --color-text-inverse: var(--color-neutral-50);

  /* â”€â”€â”€â”€â”€ Elevation â”€â”€â”€â”€â”€ */
  --shadow-1: 0 1px 2px oklch(0% 0 0 / 0.04), 0 1px 3px oklch(0% 0 0 / 0.06);
  --shadow-2: 0 4px 8px oklch(0% 0 0 / 0.06), 0 2px 4px oklch(0% 0 0 / 0.04);
  --shadow-3: 0 12px 24px oklch(0% 0 0 / 0.08), 0 4px 8px oklch(0% 0 0 / 0.04);

  /* â”€â”€â”€â”€â”€ Motion â”€â”€â”€â”€â”€ */
  --duration-instant: 80ms;
  --duration-fast: 150ms;
  --duration-base: 250ms;
  --duration-slow: 400ms;
  --duration-celebration: 800ms;
  --ease-out-soft: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Dark mode â€” explicit dark variants, not auto-inversion */
@media (prefers-color-scheme: dark) {
  @theme {
    --color-bg: oklch(13% 0.006 250);
    --color-bg-elev: oklch(17% 0.008 250);
    --color-surface: oklch(18% 0.008 250);
    --color-surface-muted: oklch(22% 0.010 250);

    --color-neutral-200: oklch(28% 0.010 250);
    --color-neutral-700: oklch(72% 0.010 250);
    --color-neutral-800: oklch(86% 0.008 250);

    --color-coral-500: oklch(70% 0.145 28);
    --color-coral-600: oklch(76% 0.150 28);

    --color-text: oklch(92% 0.005 80);
    --color-text-muted: oklch(68% 0.010 250);
  }
}

/* prefers-reduced-motion gate â€” UI-05 */
:root { --motion-scale: 1; }
@media (prefers-reduced-motion: reduce) {
  :root { --motion-scale: 0; }
}

/* Manual theme override (Settings) */
:root[data-theme="dark"] {
  /* same overrides as @media dark */
  --color-bg: oklch(13% 0.006 250);
  /* ... mirror all dark overrides */
}
:root[data-theme="light"] {
  /* explicit light reset (defaults) */
}
```

### Pattern 2: shadcn/ui CLI Init + 17 Component Install Order

**What:** Initialize shadcn/ui CLI v4 against Tailwind 4 `@theme`, then install 17 components from UI-SPEC Â§6 inventory.

**When to use:** After Tailwind 4 `@theme` block is in place. Order matters: form depends on input/label/button.

```bash
# Init shadcn/ui CLI v4 (interactive â€” answer prompts)
cd frontend
pnpm dlx shadcn@latest init
# Prompts:
#   âœ“ Style: New York   (cleaner default per shadcn 2026)
#   âœ“ Base color: Neutral
#   âœ“ CSS variables: Yes (we provide them via @theme)
#   âœ“ Components dir: src/components/ui
#   âœ“ Utils dir: src/lib/cn.ts
#   âœ“ React Server Components: No (Vite SPA)
#   âœ“ tailwind.config: skipped (Tailwind 4 = @theme only)
# Generates: components.json + cn.ts + tweaks tsconfig paths

# Add primitives (UI-SPEC Â§6.1)
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add input
pnpm dlx shadcn@latest add textarea
pnpm dlx shadcn@latest add label
pnpm dlx shadcn@latest add checkbox
pnpm dlx shadcn@latest add switch
pnpm dlx shadcn@latest add select
pnpm dlx shadcn@latest add radio-group

# Add composites (UI-SPEC Â§6.2)
pnpm dlx shadcn@latest add dialog
pnpm dlx shadcn@latest add sheet
pnpm dlx shadcn@latest add dropdown-menu
pnpm dlx shadcn@latest add form          # depends on input/label
pnpm dlx shadcn@latest add card
pnpm dlx shadcn@latest add tabs
pnpm dlx shadcn@latest add calendar       # depends on react-day-picker
pnpm dlx shadcn@latest add sonner         # toast component
pnpm dlx shadcn@latest add skeleton

# After install: customize each per UI-SPEC Â§6 variants â€” replace default classes
# with Tailwind 4 @theme tokens (no hardcoded shadcn colors).
```

**`components.json` contents (locked):**

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/styles/theme.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/cn",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

**`tsconfig.json` paths required by shadcn:**

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Pattern 3: PWA Workbox Config (FND-05, FND-06)

**What:** `vite.config.ts` registers `vite-plugin-pwa` with Workbox `generateSW` strategy. Per-pattern caching aligned with PITFALLS #2 (NetworkFirst index.html) + UI-SPEC Â§10.

**When to use:** Single config, applies app-wide.

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';

// Source: STACK.md vite-plugin-pwa, PITFALLS #2 NetworkFirst, UI-SPEC Â§10
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'prompt',           // user opt-in via toast (UI-SPEC Â§10.2) â€” never auto
      strategies: 'generateSW',
      injectRegister: 'auto',
      manifest: {
        name: 'Wellness Buddy',
        short_name: 'Wellness',
        description: 'Tracking nutrizionale e wellness',
        lang: 'it',
        start_url: '/today',
        scope: '/',
        display: 'standalone',
        orientation: 'portrait',
        theme_color: '#FAF9F6',          // light, dark via media query in index.html
        background_color: '#FAF9F6',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // PITFALL #2: never precache index.html â€” NetworkFirst it instead
        globPatterns: ['**/*.{js,css,woff2,svg,png}'],     // exclude index.html intentionally
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//],
        cleanupOutdatedCaches: true,
        skipWaiting: false,                                  // user-prompt-controlled (FND-06)
        clientsClaim: false,
        runtimeCaching: [
          // App shell â€” NetworkFirst with 3s timeout
          {
            urlPattern: ({ request }) => request.mode === 'navigate',
            handler: 'NetworkFirst',
            options: {
              cacheName: 'app-shell',
              networkTimeoutSeconds: 3,
              expiration: { maxEntries: 10, maxAgeSeconds: 7 * 24 * 3600 },
            },
          },
          // Hashed assets â€” CacheFirst long-term immutable
          {
            urlPattern: /\/assets\/.*\.(js|css|woff2)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'static-assets',
              expiration: { maxEntries: 100, maxAgeSeconds: 365 * 24 * 3600 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          // Icons + illustrations
          {
            urlPattern: /\/(icons|illustrations)\/.*\.(svg|png)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'static-images',
              expiration: { maxEntries: 50, maxAgeSeconds: 30 * 24 * 3600 },
            },
          },
          // Read API â€” NetworkFirst with 3s timeout
          {
            urlPattern: /\/api\/(plans|weekly|today)\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-reads',
              networkTimeoutSeconds: 3,
              expiration: { maxEntries: 50, maxAgeSeconds: 24 * 3600 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          // Auth + writes â€” NetworkOnly (mutation queue handles offline)
          {
            urlPattern: /\/api\/auth\/.*$/,
            handler: 'NetworkOnly',
          },
          {
            urlPattern: /\/api\/(workout|weight|errors)$/,
            handler: 'NetworkOnly',
          },
          // /version.json â€” NetworkOnly (always fresh)
          {
            urlPattern: /\/version\.json$/,
            handler: 'NetworkOnly',
          },
        ],
      },
      devOptions: {
        enabled: false,                  // SW disabled in dev to avoid debugging hell
      },
    }),
  ],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8000' },
  },
});
```

### Pattern 4: Workbox Update Flow + version.json Polling (FND-06)

**What:** Backend serves `/version.json` with build hash. Frontend polls every 5min (visible tab); on mismatch shows sonner toast with skipWaiting action.

**Backend `/version.json`:**

```python
# backend/app/api/version.py
# Source: FND-06, UI-SPEC Â§10.2
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/version.json", include_in_schema=False)
async def version():
    return {
        "version": settings.APP_VERSION,        # e.g., "1.0.0"
        "build_hash": settings.BUILD_HASH,      # injected at build via env
    }
```

**Frontend polling + toast:**

```typescript
// frontend/src/services/version.ts
// Source: FND-06, UI-SPEC Â§10.2 â€” Italian copy "Nuova versione disponibile"
import { useEffect } from 'react';
import { useRegisterSW } from 'virtual:pwa-register/react';
import { toast } from 'sonner';
import { copy } from '@/i18n/copy.it';

const CURRENT_BUILD = import.meta.env.VITE_BUILD_HASH;

async function fetchVersion(): Promise<string | null> {
  try {
    const r = await fetch('/version.json', { cache: 'no-store' });
    if (!r.ok) return null;
    const { build_hash } = await r.json();
    return build_hash;
  } catch { return null; }
}

export function useVersionPolling() {
  const { needRefresh, updateServiceWorker } = useRegisterSW({
    onRegisteredSW(swUrl, r) { /* registered */ },
    onRegisterError(error) { console.error('SW registration failed', error); },
  });

  useEffect(() => {
    let cancelled = false;
    let toastId: string | number | null = null;

    async function check() {
      if (document.hidden) return;
      const remote = await fetchVersion();
      if (!remote || cancelled) return;
      if (remote !== CURRENT_BUILD && !toastId) {
        toastId = toast.message(copy.pwa.updateHeading, {
          description: copy.pwa.updateBody,
          duration: Infinity,
          action: {
            label: copy.pwa.updateAction,
            onClick: () => updateServiceWorker(true),  // skipWaiting + reload
          },
          cancel: { label: copy.pwa.updateDismiss, onClick: () => { /* postpone */ } },
        });
      }
    }

    check();
    const interval = setInterval(check, 5 * 60 * 1000);
    document.addEventListener('visibilitychange', check);
    return () => {
      cancelled = true;
      clearInterval(interval);
      document.removeEventListener('visibilitychange', check);
    };
  }, [updateServiceWorker]);
}
```

### Pattern 5: Dexie Schema with Versioning + Upgrade Hooks (FND-07)

**What:** Single Dexie database with `cache_*` mirror tables, `mutation_queue` outbox, `drafts` work-in-progress. UUIDs server-generated.

```typescript
// frontend/src/db/dexie.ts
// Source: FND-07, ARCHITECTURE.md Â§5.4, PITFALLS #5
import Dexie, { type EntityTable } from 'dexie';

// All IDs are server-issued UUIDs â€” never auto-increment (PITFALLS #5)
export interface CachedUser {
  id: string;              // server UUID
  email: string;
  username: string;
  role: 'admin' | 'user';
  group_id: string | null;
  timezone: string;        // IANA, e.g., 'Europe/Rome'
}

export interface CachedPlan {
  id: string;
  user_id: string;
  name: string;
  parsed_json: unknown;    // PlanParsedSchema
  uploaded_at: string;     // ISO 8601 UTC
  is_active: boolean;
}

export interface CachedToday {
  date: string;            // YYYY-MM-DD user TZ
  user_id: string;
  meals_completed: Record<string, boolean>;  // meal_type â†’ completed
  fetched_at: string;      // ISO 8601
}

export interface CachedWorkoutLog {
  id: string;
  user_id: string;
  date: string;            // YYYY-MM-DD
  trained: boolean;
  duration_min: number | null;
  calories_burned: number | null;
  workout_type: string | null;
  notes: string | null;
  updated_at: string;
}

export interface CachedWeightLog {
  id: string;
  user_id: string;
  date: string;
  weight_kg: number;
  updated_at: string;
}

export interface QueuedMutation {
  id: string;              // crypto.randomUUID() â€” local only
  endpoint: string;
  method: 'POST' | 'PATCH' | 'DELETE';
  body: unknown;
  created_at: number;
  retries: number;
  last_error: string | null;
}

export interface Draft {
  key: string;             // e.g., 'workout-form-2026-05-01'
  payload: unknown;
  updated_at: number;
}

// Dexie database with versioning
export class WellnessBuddyDB extends Dexie {
  cache_users!: EntityTable<CachedUser, 'id'>;
  cache_plans!: EntityTable<CachedPlan, 'id'>;
  cache_today!: EntityTable<CachedToday, 'date'>;
  cache_workout_log!: EntityTable<CachedWorkoutLog, 'id'>;
  cache_weight_log!: EntityTable<CachedWeightLog, 'id'>;
  mutation_queue!: EntityTable<QueuedMutation, 'id'>;
  drafts!: EntityTable<Draft, 'key'>;

  constructor() {
    super('wellness-buddy');

    // v1 â€” Phase 1 baseline
    this.version(1).stores({
      cache_users: 'id, email',
      cache_plans: 'id, user_id, is_active',
      cache_today: 'date, user_id',
      cache_workout_log: 'id, [user_id+date]',
      cache_weight_log: 'id, [user_id+date]',
      mutation_queue: 'id, created_at',
      drafts: 'key, updated_at',
    });

    // PITFALL #5: Future schema bumps DROP cache_* and re-fetch from server
    // (mutation_queue stores opaque HTTP requests â€” survives schema changes)
    // Example future v2 upgrade:
    // this.version(2).stores({
    //   cache_today: 'date, user_id, status_indicator',  // new field
    // }).upgrade(async (tx) => {
    //   await tx.table('cache_today').clear();   // drop, re-fetch
    // });
  }

  /**
   * Phase 1 helper: detect Dexie-empty-but-JWT-valid â†’ trigger full resync
   * Source: FND-08, PITFALLS #1
   */
  async isEmptyButShouldHaveData(): Promise<boolean> {
    const userCount = await this.cache_users.count();
    const planCount = await this.cache_plans.count();
    return userCount === 0 && planCount === 0;
  }
}

export const db = new WellnessBuddyDB();
```

**Mutation queue helper:**

```typescript
// frontend/src/lib/mutationQueue.ts
// Source: ARCHITECTURE.md Pattern 1, PITFALLS #5
import { db } from '@/db/dexie';
import { apiClient } from '@/services/api';
import { toast } from 'sonner';
import { copy } from '@/i18n/copy.it';

export async function enqueueMutation(
  m: Omit<QueuedMutation, 'id' | 'created_at' | 'retries' | 'last_error'>
) {
  await db.mutation_queue.add({
    id: crypto.randomUUID(),
    created_at: Date.now(),
    retries: 0,
    last_error: null,
    ...m,
  });
}

export async function flushQueue() {
  const items = await db.mutation_queue.orderBy('created_at').toArray();
  for (const item of items) {
    try {
      await apiClient.request({ url: item.endpoint, method: item.method, data: item.body });
      await db.mutation_queue.delete(item.id);
    } catch (e: any) {
      if (e.response?.status === 409) {
        await db.mutation_queue.delete(item.id);
        toast.error(copy.errors.conflict, { description: copy.errors.conflictHint });
        continue;
      }
      if (item.retries >= 5) {
        await db.mutation_queue.update(item.id, { last_error: String(e), retries: item.retries + 1 });
        // dead-letter â€” surface to user
        toast.error(copy.errors.syncFailed);
        break;
      }
      await db.mutation_queue.update(item.id, { retries: item.retries + 1, last_error: String(e) });
      break; // preserve order
    }
  }
}

window.addEventListener('online', () => { void flushQueue(); });
```

### Pattern 6: navigator.storage.persist() Flow (FND-08, D-15)

```typescript
// frontend/src/lib/persistStorage.ts
// Source: FND-08, D-15, PITFALLS #1
import { toast } from 'sonner';
import { copy } from '@/i18n/copy.it';

export async function requestPersistentStorage(): Promise<boolean> {
  if (!navigator.storage?.persist) return false;
  const already = await navigator.storage.persisted();
  if (already) return true;
  const granted = await navigator.storage.persist();
  if (!granted) {
    toast.warning(copy.pwa.persistDeniedHeading, {
      description: copy.pwa.persistDeniedBody,
    });
  }
  return granted;
}

export async function getStorageEstimate(): Promise<{ used: number; quota: number } | null> {
  if (!navigator.storage?.estimate) return null;
  const { usage = 0, quota = 0 } = await navigator.storage.estimate();
  return { used: usage, quota };
}
```

**When called:** From `<PersistStorageWelcome />` full-screen welcome that appears post-first-login (D-15). Component shows hero illustration + Italian CTA "Abilita storage offline" â†’ on click calls `requestPersistentStorage()`. Show "Ultima sincronizzazione" trust signal in `SyncStatusPip` using `getStorageEstimate()` for telemetry.

### Pattern 7: SQLAlchemy 2 Async Models + Mapped Declarative

**Concrete code for User + Group:**

```python
# backend/app/models/base.py
# Source: SQLAlchemy 2.0 docs, MOD-09 TIMESTAMPTZ everywhere
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime
from typing import Annotated

class Base(DeclarativeBase):
    pass

# Type alias for TIMESTAMPTZ default-now
TimestampTZ = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    ),
]
```

```python
# backend/app/models/user.py
# Source: MOD-01, MOD-09, ARCHITECTURE.md Â§4 Pattern 4
from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampTZ

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")  # 'admin' | 'user'
    group_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL"), nullable=True
    )
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Rome")  # IANA
    created_at: Mapped[TimestampTZ]

    group: Mapped["Group | None"] = relationship(back_populates="users")
```

```python
# backend/app/models/variant.py
# Source: MOD-04, ARCHITECTURE.md Pattern 4 visibility enum, MOD-10 indexes
from __future__ import annotations
from datetime import date, datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Date, Integer, Index, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampTZ

class Visibility(str, PyEnum):
    PRIVATE = "private"
    GROUP_SHARED = "group_shared"

class WeeklyPlanVariant(Base):
    __tablename__ = "weekly_plan_variants"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"))
    plan_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("nutrition_plans.id"))
    week_start: Mapped[date] = mapped_column(Date)
    day_of_week: Mapped[int] = mapped_column(Integer)        # 0=Mon..6=Sun
    meal_type: Mapped[str] = mapped_column(String(20))       # breakfast|lunch|dinner|snack
    variant_key: Mapped[str] = mapped_column(String(20))     # 'A' | 'B' | 'pasta'
    visibility: Mapped[Visibility] = mapped_column(
        SAEnum(Visibility, name="visibility_enum"),
        default=Visibility.PRIVATE,
    )
    completed: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)  # LWW conflict
    updated_at: Mapped[TimestampTZ]
    created_at: Mapped[TimestampTZ]

    __table_args__ = (
        Index("ix_weekly_user_week", "user_id", "week_start"),
        Index("ix_weekly_group_share", "week_start", "visibility"),
    )
```

**Async session config:**

```python
# backend/app/core/database.py
# Source: D-29 pool 15/10, SQLAlchemy 2 async docs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,                      # postgresql+asyncpg://user:pw@host/WellnessBuddy
    pool_size=15,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO,                     # True in dev only
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
```

### Pattern 8: Alembic Baseline Migration (D-30)

**Async env.py:**

```python
# backend/alembic/env.py
# Source: D-30, Alembic async + SQLAlchemy 2 docs
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.core.config import settings
from app.models.base import Base
import app.models  # noqa: F401  ensure all models registered

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

**Generate baseline:**

```bash
cd backend
uv run alembic revision --autogenerate -m "baseline"
# Verify generated 0000_baseline.py contains:
#   - users, groups, nutrition_plans, weekly_plan_variants
#   - workout_log, weight_log, shopping_list_state
#   - invite_tokens, refresh_tokens (rotation), audit_log
#   - All indexes per MOD-10
#   - Partial unique index: WHERE is_active = true on (user_id) for nutrition_plans
mv alembic/versions/*_baseline.py alembic/versions/0000_baseline.py
uv run alembic upgrade head
```

### Pattern 9: Auth â€” JWT Refresh Rotation + Singleton Promise + 10s Grace Window

**Backend security.py:**

```python
# backend/app/core/security.py
# Source: AUTH-04..AUTH-08, ARCHITECTURE.md Pattern 5, PITFALLS #4
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(p: str) -> str: return pwd_context.hash(p)
def verify_password(p: str, h: str) -> bool: return pwd_context.verify(p, h)

def create_access_token(user_id: UUID, expires_in: timedelta = timedelta(minutes=15)) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + expires_in, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: UUID, family_id: UUID, jti: UUID,
                          expires_in: timedelta = timedelta(days=7)) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id), "family": str(family_id), "jti": str(jti),
        "iat": now, "exp": now + expires_in, "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
```

**Refresh rotation service (10s grace window â€” PITFALLS #4):**

```python
# backend/app/services/auth_service.py
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.refresh import RefreshToken
from app.core.security import create_access_token, create_refresh_token, decode_token

GRACE_WINDOW = timedelta(seconds=10)

async def rotate_refresh(session: AsyncSession, refresh_jwt: str) -> tuple[str, str]:
    """Rotate refresh token. Returns (new_access, new_refresh).
    10s idempotent grace: reuse within 10s of rotation returns same new pair.
    """
    try:
        payload = decode_token(refresh_jwt)
    except Exception:
        raise HTTPException(401, {"detail": "Token non valido", "code": "invalid_token"})

    if payload.get("type") != "refresh":
        raise HTTPException(401, {"detail": "Token non valido", "code": "invalid_token"})

    user_id = UUID(payload["sub"])
    family_id = UUID(payload["family"])
    jti = UUID(payload["jti"])

    row = (await session.scalars(
        select(RefreshToken).where(RefreshToken.jti == jti)
    )).first()

    if not row:
        raise HTTPException(401, {"detail": "Token scaduto", "code": "expired"})

    if row.revoked:
        # Reuse detection within grace window â€” return cached new pair (idempotent)
        if row.replaced_at and (datetime.now(timezone.utc) - row.replaced_at) < GRACE_WINDOW:
            return row.cached_access, row.cached_refresh
        # Real reuse â†’ revoke entire family
        await session.execute(
            select(RefreshToken).where(RefreshToken.family_id == family_id)
            .execution_options(synchronize_session=False)
        )
        # ... mark all family tokens revoked
        raise HTTPException(401, {"detail": "Sessione invalidata", "code": "family_revoked"})

    # Issue new pair
    new_jti = uuid4()
    new_refresh = create_refresh_token(user_id, family_id, new_jti)
    new_access = create_access_token(user_id)

    # Store new
    session.add(RefreshToken(jti=new_jti, family_id=family_id, user_id=user_id))
    # Mark old revoked + cache new pair for grace window
    row.revoked = True
    row.replaced_at = datetime.now(timezone.utc)
    row.cached_access = new_access
    row.cached_refresh = new_refresh

    await session.commit()
    return new_access, new_refresh
```

**Frontend singleton refresh promise:**

```typescript
// frontend/src/lib/refreshTokenAtomic.ts
// Source: AUTH-07, PITFALLS #4 â€” single in-flight promise resolves all 401 awaiters
import { useAuthStore } from '@/stores/auth';

let inflightRefresh: Promise<string> | null = null;

export function refreshTokenAtomic(): Promise<string> {
  if (inflightRefresh) return inflightRefresh;
  inflightRefresh = (async () => {
    try {
      const res = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',          // HttpOnly refresh cookie
      });
      if (!res.ok) {
        useAuthStore.getState().clear();
        throw new Error('refresh failed');
      }
      const { access_token } = await res.json();
      useAuthStore.getState().setAccessToken(access_token);
      return access_token;
    } finally {
      // Reset after settle (success or fail) so next 401 starts fresh
      setTimeout(() => { inflightRefresh = null; }, 0);
    }
  })();
  return inflightRefresh;
}
```

**API client interceptor (Zustand):**

```typescript
// frontend/src/services/api.ts
import { useAuthStore } from '@/stores/auth';
import { refreshTokenAtomic } from '@/lib/refreshTokenAtomic';

export const apiClient = {
  async request<T>(opts: { url: string; method?: string; data?: unknown }): Promise<T> {
    const access = useAuthStore.getState().accessToken;
    let res = await fetch(opts.url, {
      method: opts.method ?? 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(access ? { Authorization: `Bearer ${access}` } : {}),
      },
      body: opts.data ? JSON.stringify(opts.data) : undefined,
      credentials: 'include',
    });
    if (res.status === 401 && access) {
      // Single concurrent refresh â€” all parallel 401s await the same promise
      const newAccess = await refreshTokenAtomic();
      res = await fetch(opts.url, {
        method: opts.method ?? 'GET',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${newAccess}` },
        body: opts.data ? JSON.stringify(opts.data) : undefined,
        credentials: 'include',
      });
    }
    if (!res.ok) {
      const detail = await res.json().catch(() => ({ detail: 'Errore', code: 'unknown' }));
      throw { response: { status: res.status, data: detail } };
    }
    return res.json();
  },
};
```

**Zustand auth store:**

```typescript
// frontend/src/stores/auth.ts
// Source: AUTH-04 access in-mem
import { create } from 'zustand';

interface AuthState {
  accessToken: string | null;
  user: { id: string; email: string; role: 'admin' | 'user' } | null;
  setAccessToken: (t: string) => void;
  setUser: (u: AuthState['user']) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setAccessToken: (accessToken) => set({ accessToken }),
  setUser: (user) => set({ user }),
  clear: () => set({ accessToken: null, user: null }),
}));
```

### Pattern 10: MD Parser Concrete Implementation (PLAN-01..PLAN-06)

**Normalizer pipeline:**

```python
# backend/app/parsers/normalizer.py
# Source: PLAN-03, PITFALLS #6
import unicodedata
import re

# CRITICAL: 'utf-8-sig' decodes WITH BOM stripping; 'utf-8' does NOT.
# When reading bytes from UploadFile, use:
#   text = raw_bytes.decode('utf-8-sig')   # NOT 'utf-8'

_NBSP_REGEX = re.compile(r'[Â â€‡â€¯â ]')        # NBSP variants
_SMART_QUOTE_MAP = str.maketrans({
    'â€˜': "'", 'â€™': "'", 'â€š': "'", 'â€›': "'",
    'â€œ': '"', 'â€': '"', 'â€ž': '"', 'â€Ÿ': '"',
    'â€“': '-', 'â€”': '-',                   # en/em dash
    'â€¦': '...',                                # ellipsis
})

def normalize_md(raw_bytes: bytes) -> str:
    """Normalize MD bytes to clean parseable text.
    Pipeline: utf-8-sig decode â†’ CRLFâ†’LF â†’ NFC â†’ NBSPâ†’space â†’ smart-punctâ†’ASCII
    """
    # 1. BOM strip (PITFALL: must use 'utf-8-sig' not 'utf-8')
    text = raw_bytes.decode('utf-8-sig', errors='replace')
    # 2. Line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # 3. NFC normalize (macOS often emits NFD)
    text = unicodedata.normalize('NFC', text)
    # 4. NBSP â†’ regular space
    text = _NBSP_REGEX.sub(' ', text)
    # 5. Smart punctuation â†’ ASCII
    text = text.translate(_SMART_QUOTE_MAP)
    return text
```

**Plan parser:**

```python
# backend/app/parsers/plan_parser.py
# Source: PLAN-02, PLAN-04, PLAN-05, PLAN-06
import re
from dataclasses import dataclass, field
from app.parsers.normalizer import normalize_md
from app.schemas.plan_parsed import PlanParsedSchema

# Canonical section stems (lowercase, accent-stripped). Match by stem.
SECTION_STEMS = {
    "dati personali": "personal_data",
    "calcolo calorico": "macro_target",            # matches "CALCOLO CALORICO E MACRO TARGET"
    "struttura giornaliera": "daily_structure",
    "colazione": "breakfast",
    "pranzi": "lunches",
    "cene": "dinners",
    "spuntino pomeriggio": "snacks",
    "supplementazione": "supplements",
    "proiezione peso": "weight_projection",
    "regole fondamentali": "rules",
}

# Heading regex: ## or # plus optional leading emoji/decoration
_HEADING_RE = re.compile(r'^(#{1,6})\s*(.+?)\s*$', re.MULTILINE)
_EMOJI_PREFIX_RE = re.compile(r'^[\W_]+', flags=re.UNICODE)  # strip leading non-word

def _heading_stem(heading_text: str) -> str:
    """Strip emoji prefix, decoration, lowercase, collapse spaces."""
    s = _EMOJI_PREFIX_RE.sub('', heading_text)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

@dataclass
class ParseReport:
    warnings: list[str] = field(default_factory=list)
    unrecognized_headings: list[str] = field(default_factory=list)

def parse_and_validate(raw_bytes: bytes) -> tuple[PlanParsedSchema, ParseReport]:
    text = normalize_md(raw_bytes)
    sections = _split_sections(text)
    report = ParseReport()
    raw_dict = {}
    for heading, body in sections.items():
        stem = _heading_stem(heading)
        # Match by stem prefix â€” "calcolo calorico" matches "calcolo calorico e macro target"
        matched = next((target for s, target in SECTION_STEMS.items() if stem.startswith(s)), None)
        if matched:
            raw_dict[matched] = _parse_section(matched, body, report)
        else:
            report.unrecognized_headings.append(heading)
    schema = PlanParsedSchema.model_validate(raw_dict)
    return schema, report

def _split_sections(text: str) -> dict[str, str]:
    """Split MD into {heading: body} dict using regex."""
    parts = []
    matches = list(_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        parts.append((m.group(2), text[m.end():end].strip()))
    return dict(parts)

def _parse_section(name: str, body: str, report: ParseReport) -> dict:
    # Per-section regex parsers â€” implementation deferred to plan_sections.py
    # Stub returns raw body for now
    return {"raw": body}
```

**Strict Pydantic v2 schema:**

```python
# backend/app/schemas/plan_parsed.py
# Source: PLAN-06
from pydantic import BaseModel, Field

class PersonalData(BaseModel):
    name: str
    age: int | None = None
    current_weight_kg: float | None = None
    target_weight_kg: float | None = None

class Macros(BaseModel):
    kcal: int = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0

class Ingredient(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None

class MealOption(BaseModel):
    key: str
    title: str
    ingredients: list[Ingredient] = Field(default_factory=list)
    macros: Macros = Field(default_factory=Macros)

class PlanParsedSchema(BaseModel):
    personal_data: PersonalData | None = None
    macro_target: Macros = Field(default_factory=Macros)
    daily_structure: list[dict] = Field(default_factory=list)
    breakfast: MealOption | None = None
    lunches: dict[str, list[MealOption]] = Field(default_factory=dict)
    dinners: dict[str, list[MealOption]] = Field(default_factory=dict)
    snacks: list[MealOption] = Field(default_factory=list)
    supplements: list[dict] = Field(default_factory=list)
    weight_projection: list[dict] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
```

### Pattern 11: AI Provider DI Sketch (AI-01..AI-07)

```python
# backend/app/ai/base.py
# Source: AI-01, ARCHITECTURE.md Pattern 2
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def generate_meal_suggestion(self, **kwargs) -> str: ...
    @abstractmethod
    async def analyze_week_progress(self, **kwargs) -> str: ...
    @abstractmethod
    async def generate_shopping_tips(self, **kwargs) -> str: ...
    @abstractmethod
    async def chat(self, **kwargs) -> str: ...
    @property
    @abstractmethod
    def is_available(self) -> bool: ...
```

```python
# backend/app/ai/null_provider.py
# Source: AI-02, AI-04 â€” 501 Italian
from fastapi import HTTPException
from app.ai.base import AIProvider

NULL_RESPONSE = {"detail": "AI non disponibile", "code": "ai_unavailable"}

class NullProvider(AIProvider):
    @property
    def is_available(self) -> bool: return False

    async def generate_meal_suggestion(self, **_): raise HTTPException(501, NULL_RESPONSE)
    async def analyze_week_progress(self, **_): raise HTTPException(501, NULL_RESPONSE)
    async def generate_shopping_tips(self, **_): raise HTTPException(501, NULL_RESPONSE)
    async def chat(self, **_): raise HTTPException(501, NULL_RESPONSE)
```

```python
# backend/app/ai/factory.py
# Source: AI-03, AI-07
from app.ai.base import AIProvider
from app.ai.null_provider import NullProvider
from app.core.config import settings

def build_provider() -> AIProvider:
    name = settings.AI_PROVIDER  # 'null' Phase 1 default
    if name == "null":
        return NullProvider()
    # Phase 5 will add: ollama, openai, anthropic
    raise ValueError(f"unknown AI_PROVIDER: {name}")
```

```python
# backend/app/main.py
# Source: AI-03 lifespan, FastAPI lifespan docs
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.ai.factory import build_provider
from app.core.logging import configure_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    app.state.ai_provider = build_provider()
    yield
    # cleanup if needed

app = FastAPI(title="Wellness Buddy API", lifespan=lifespan)

# ... include routers
```

```python
# backend/app/core/deps.py
# Source: AI-03 Depends pattern
from fastapi import Request
from app.ai.base import AIProvider

def get_ai_provider(request: Request) -> AIProvider:
    return request.app.state.ai_provider
```

```python
# backend/app/api/ai.py
# Source: AI-04 â€” endpoints exist Phase 1, return 501 via NullProvider
from fastapi import APIRouter, Depends
from app.ai.base import AIProvider
from app.core.deps import get_ai_provider, get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/ai", tags=["ai"])

@router.post("/meal-suggestion")
async def meal_suggestion(
    user: User = Depends(get_current_user),
    ai: AIProvider = Depends(get_ai_provider),
):
    return {"suggestion": await ai.generate_meal_suggestion()}

@router.post("/week-analysis")
async def week_analysis(
    user: User = Depends(get_current_user),
    ai: AIProvider = Depends(get_ai_provider),
):
    return {"analysis": await ai.analyze_week_progress()}

@router.post("/shopping-tips")
async def shopping_tips(
    user: User = Depends(get_current_user),
    ai: AIProvider = Depends(get_ai_provider),
):
    return {"tips": await ai.generate_shopping_tips()}

@router.post("/chat")
async def chat(
    user: User = Depends(get_current_user),
    ai: AIProvider = Depends(get_ai_provider),
):
    return {"response": await ai.chat()}
```

### Pattern 12: Italian copy.it.ts Structure (FND-09)

```typescript
// frontend/src/i18n/copy.it.ts
// Source: FND-09, UI-SPEC Â§7.2 â€” ~80 strings locked
// Type-safe via `as const` + literal types. Refactor to react-i18next deferred v2.

export const copy = {
  auth: {
    loginHeading: 'Accedi a Wellness Buddy',
    emailLabel: 'Email',
    emailPlaceholder: 'nome@esempio.it',
    passwordLabel: 'Password',
    submitCta: 'Accedi',
    forgotLink: 'Password dimenticata?',
    invalidCreds: 'Email o password non corretti. Riprova.',
    locked: 'Account momentaneamente non disponibile. Riprova tra qualche minuto.',
    offlineLogin: 'Nessuna connessione. Controlla la rete e riprova.',
    sessionExpired: 'Sessione scaduta dopo 7 giorni di inattivitÃ . Accedi di nuovo.',
    logoutConfirm: 'Vuoi davvero uscire?',
    logoutCta: 'Esci',
    logoutCancel: 'Annulla',
    logoutToast: 'Sei uscito.',
  },
  invite: {
    heading: 'Crea il tuo account',
    subheading: 'Sei stato invitato a Wellness Buddy.',
    nameLabel: 'Come ti chiami',
    submitCta: 'Crea account',
    tokenExpired: 'Questo invito Ã¨ scaduto. Chiedi all\'amministratore un nuovo link.',
    tokenInvalid: 'Questo invito non Ã¨ valido. Chiedi all\'amministratore un nuovo link.',
  },
  today: {
    greeting: {
      morning: 'Buongiorno, {nome}',
      afternoon: 'Buon pomeriggio, {nome}',
      evening: 'Buonasera, {nome}',
      night: 'Ciao, {nome}',
    },
    emptyNoPlan: { heading: 'Nessun piano attivo', body: 'Carica il tuo piano nutrizionale per iniziare.', cta: 'Carica piano' },
    emptyDayBlank: { heading: 'Niente registrato oggi', body: 'Quando segni i pasti, qui vedi i progressi.' },
    mealMarkCta: 'Segna pasto',
    mealCompletedLabel: 'Pasto registrato',
    macroKcal: 'kcal', macroProtChip: 'prot', macroProtFull: 'proteine',
    macroCarbChip: 'carbo', macroCarbFull: 'carboidrati', macroFat: 'grassi',
  },
  weight: {
    heading: 'Pesata di oggi',
    inputLabel: 'Peso (kg)',
    submitCta: 'Salva peso',
    successToast: 'Peso registrato.',
    editToast: 'Peso aggiornato.',
    deleteConfirm: 'Cancellare la pesata di {data}?',
    deleteCta: 'Elimina',
    deleteSuccess: 'Pesata eliminata.',
  },
  workout: {
    heading: 'Allenamento di oggi',
    toggleLabel: 'Hai allenato oggi?',
    durationLabel: 'Durata (minuti)',
    typeLabel: 'Tipo',
    typePlaceholder: 'es. corsa, yoga, palestra',
    caloriesLabel: 'Calorie bruciate',
    caloriesHelper: 'Opzionale',
    notesLabel: 'Note',
    submitCta: 'Salva allenamento',
    successToast: 'Allenamento registrato.',
  },
  plans: {
    heading: 'Carica piano nutrizionale',
    dropzoneIdle: 'Trascina qui il file .md o tocca per scegliere',
    dropzoneDragging: 'Rilascia per caricare',
    parsingState: 'Sto leggendo il piano...',
    parseWarningsHeading: 'Sezioni non riconosciute',
    parseWarningsBody: 'Il piano Ã¨ stato letto, ma queste sezioni non sono state riconosciute: {list}. Puoi attivarlo comunque o annullare.',
    diffHeading: 'Differenze rispetto al piano attivo',
    activateCta: 'Attiva piano',
    cancelCta: 'Annulla',
    activateConfirm: 'Sostituire il piano attivo con quello caricato? Il piano precedente verrÃ  archiviato.',
    activateSuccess: 'Piano attivato.',
    errorBadFileType: 'Solo file .md sono supportati.',
    errorTooLarge: 'Il file supera il limite di 1 MB.',
    errorParseFailed: 'Non sono riuscito a leggere il piano. Verifica che il formato sia corretto.',
  },
  pwa: {
    installHeading: 'Installa Wellness Buddy',
    installBody: 'Aggiungilo alla schermata Home per usarlo come app.',
    installCta: 'Mostra come fare',
    installStep1: 'Tocca il pulsante Condividi nella barra di Safari.',
    installStep2: 'Scorri e tocca "Aggiungi a Home".',
    installStep3: 'Conferma toccando "Aggiungi".',
    installDismiss: 'PiÃ¹ tardi',
    updateHeading: 'Nuova versione disponibile',
    updateBody: 'Ricarica per aggiornare.',
    updateAction: 'Ricarica',
    updateDismiss: 'PiÃ¹ tardi',
    persistDeniedHeading: 'Storage offline non abilitato',
    persistDeniedBody: 'I tuoi dati potrebbero essere cancellati dopo 7 giorni di inattivitÃ . Apri l\'app regolarmente.',
  },
  ai: {
    placeholderHeading: 'AI in arrivo',
    placeholderBody: 'L\'assistente AI sarÃ  disponibile presto. Puoi usare l\'app senza problemi anche ora.',
  },
  sync: {
    synced: 'Sincronizzato',
    pending: 'In sincronizzazione',
    error: 'Sincronizzazione non riuscita',
    offline: 'Offline',
    tooltip: 'Ultima sincronizzazione: {time}',
    offlineToast: 'Nessuna connessione. Le modifiche verranno inviate quando torni online.',
  },
  errors: {
    forbidden: 'Non hai accesso a questa sezione.',
    notFound: 'Pagina non trovata.',
    generic500: 'Qualcosa non ha funzionato. Riprova tra poco.',
    networkOffline: 'Nessuna connessione. Le modifiche verranno inviate quando torni online.',
    boundaryHeading: 'Qualcosa non ha funzionato',
    boundaryBody: 'Ricarica la pagina o torna a Oggi.',
    boundaryReloadCta: 'Ricarica',
    boundaryHomeCta: 'Torna a Oggi',
    conflict: 'Modificato da un altro utente',
    conflictHint: 'Ricarica per vedere l\'ultima versione.',
    syncFailed: 'Sincronizzazione non riuscita. Riprova piÃ¹ tardi.',
  },
  settings: {
    themeHeading: 'Tema',
    themeLight: 'Chiaro', themeDark: 'Scuro', themeSystem: 'Sistema',
    profileHeading: 'Profilo',
    languageHeading: 'Lingua',
    languageValue: 'Italiano',
    languageNote: 'Solo italiano in questa versione.',
    logoutCta: 'Esci',
  },
  appBar: { today: 'Oggi', history: 'Storico', plan: 'Piano', settings: 'Impostazioni' },
  appBoot: { resyncMessage: 'Sto ricaricando i tuoi dati...' },
} as const;

export type Copy = typeof copy;
```

### Anti-Patterns to Avoid

- **Hardcoded hex/font-size/radius:** every value goes through `@theme` token. ESLint rule `no-restricted-syntax` to ban `style={{ color: '#...' }}` literals.
- **Cache-first on `index.html`:** PITFALL #2 â€” always NetworkFirst.
- **localStorage for refresh token:** PITFALLS #4 + ARCHITECTURE.md Anti-Pattern 2 â€” HttpOnly cookie only.
- **Auto-incremented Dexie PKs:** PITFALLS #5 â€” server UUIDs only.
- **`group_id` in JWT claims:** PITFALLS #3 â€” always re-look-up from DB.
- **Single `get_current_user` for cross-user reads:** ARCHITECTURE Anti-Pattern 5 â€” separate dependency for cross-user access (Phase 2).
- **Direct AI SDK calls in services:** ARCHITECTURE Anti-Pattern 1 â€” always via `Depends(get_ai_provider)`.
- **`utf-8` decode for MD upload:** PITFALLS #6 â€” must be `utf-8-sig` to strip BOM.
- **Per-request AI provider construction:** ARCHITECTURE Anti-Pattern 4 â€” singleton at lifespan startup.
- **Validating MD inline in API endpoint:** ARCHITECTURE Anti-Pattern 6 â€” `parse_and_validate` in `parsers/`.
- **`!` in error messages:** UI-SPEC Â§7.1 / UI-17 â€” reserved for celebratory only.
- **Vanilla shadcn defaults:** UI-03 â€” every component customized after `add`.
- **Animations without `--motion-scale`:** UI-05 â€” must short-circuit when `prefers-reduced-motion: reduce`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JWT encode/decode | Custom HMAC | `python-jose[cryptography]` | Standard JWT lib, FastAPI-integrated |
| Password hash | Custom bcrypt wrapper | `passlib[bcrypt]` rounds=12 | Constant-time, pepper handling |
| MD AST parsing | Regex line-by-line | `python-markdown` for AST + custom regex on top | python-markdown handles GFM tables, lists, code |
| Service Worker | Hand-written SW | `vite-plugin-pwa` + Workbox 7 | Workbox handles cache strategies, navigation fallback, precache manifest |
| Form state + validation | useState + manual validation | `react-hook-form` + `zod` + `@hookform/resolvers` | Min re-renders, type-safe schemas, ARIA-correct error wiring |
| Toast notifications | Custom portal + animation | `sonner` | shadcn default, accessible, beautiful |
| IndexedDB direct access | Raw `indexedDB.open` | `dexie` v4.4 | Schema versioning, hooks, observable queries, transactions |
| Optimistic mutations | Manual cache + rollback | `@tanstack/react-query` `useMutation` `onMutate/onError` | Standard pattern with cache invalidation |
| Date math | Custom moment-style | `date-fns` v4 | Tree-shakable, IANA tz support |
| Italian number/date format | `toLocaleString()` ad-hoc | `Intl.NumberFormat('it-IT')` + `Intl.DateTimeFormat('it-IT')` + `Intl.Collator('it')` | Standard, NFC-aware sorting |
| Async PostgreSQL driver | `psycopg` sync | `asyncpg` via SQLAlchemy 2 async | Native async, faster than psycopg async |
| DB migrations | SQL files manually applied | `alembic` async env.py | Schema versioning, autogenerate, rollback |
| File upload streaming | Manual multipart | `python-multipart` (FastAPI handles) | Standard FastAPI |
| Logging structured JSON | `logging` module manual | `structlog` v24+ | JSON output, request-ID context, processor pipeline |
| Charts (line, area, bar) | D3 from scratch | `recharts` v3 | Declarative JSX, SVG, Tailwind-themeable |
| Calendar / date picker | Custom range picker | `react-day-picker` v9 + shadcn `Calendar` wrapper | WCAG 2.1 AA, headless, keyboard nav |
| Accessibility primitives | Custom focus traps | shadcn/ui (Radix UI under the hood) | WAI-ARIA out of the box |
| Singleton refresh promise | Per-tab event bus | Module-scoped `Promise<T> \| null` reset on settle | Simplest correct pattern |
| Test postgres container | Manual Docker setup per test | `pytest-postgresql` | Fixture-managed ephemeral postgres, parallel-safe |
| a11y testing | Manual audit | `@axe-core/playwright` | CI-enforceable, AA gates |
| Visual regression | Custom screenshot diff | Playwright `toHaveScreenshot()` | Built-in pixel diff |

**Key insight:** Phase 1 has zero novel cryptography, zero novel persistence, zero novel UI primitives. Every "hand-roll" temptation is a worse-than-existing solution. The scope discipline is `compose libraries`, not `re-implement`.

## Runtime State Inventory

> Greenfield phase â€” Phase 1 is the **first phase**, no prior runtime state exists in production. This section is omitted as a discovery exercise. Whenever Phase 1 introduces NEW runtime state (Dexie schema v1, refresh_tokens table, Alembic baseline), the planner should ensure all five categories are documented for downstream phases:

| Category | Phase 1 baseline established | Future phases must update |
|----------|-----------------------------|--------------------------|
| Stored data | PostgreSQL `WellnessBuddy` DB created manually; Alembic baseline applied | Schema migrations only via Alembic |
| Live service config | NSSM service `WellnessBuddyAPI`; IIS site `wellness-buddy.epartner.it` | Document in DEPLOY.md |
| OS-registered state | NSSM service description "Wellness Buddy API" | Re-register if name/path changes |
| Secrets/env vars | `SECRET_KEY` (token_hex 32), `DATABASE_URL`, `AI_PROVIDER=null`, `VITE_VAPID_PUBLIC_KEY` (Phase 3) | DPAPI-encrypted on Windows |
| Build artifacts | None Phase 1 (greenfield); `frontend/dist/` produced by `pnpm build` | `dist/` regenerated each deploy |

**Nothing pre-existing in repo to migrate** â€” verified by reading `d:/Develop/AI/WellnessBuddy/` (only `.planning/`, `CLAUDE.md`, `docs/PROMPT_CONTRACT_WELLNESS_BUDDY.md`).

## Common Pitfalls

### Pitfall 1: Tailwind 4 + shadcn/ui v4 Setup Quirks (2026)

**What goes wrong:** shadcn/ui CLI generates components expecting `tailwind.config.ts` and CSS variables in legacy format; Tailwind 4 expects `@theme` block in CSS. Mismatch â†’ components render with wrong colors / no theming.

**Why it happens:** shadcn CLI auto-detects v3 layout. Components.json must explicitly point to `theme.css`, not `tailwind.config.ts`.

**How to avoid:**
- Set up `theme.css` with `@theme` block FIRST (before `pnpm dlx shadcn init`).
- In `components.json`, set `"tailwind": { "config": "", "css": "src/styles/theme.css", "cssVariables": true }`.
- After each `shadcn add`, manually replace any hardcoded colors (`bg-slate-100` etc.) with `@theme` token references.
- Add ESLint rule banning hardcoded color classes outside `components/ui/`.

**Warning signs:** Components render with default Tailwind palette instead of OKLCH coral/neutral. Dark mode toggle has no effect.

**Phase to address:** Plan 5 (Frontend Skeleton) before any feature plan touches UI.

### Pitfall 2: vite-plugin-pwa on Windows + Husky pre-commit

**What goes wrong:** Husky `pre-commit` shell scripts fail with `\r\n` line endings on Windows; vite-plugin-pwa generates SW with paths containing backslashes that fail in browser.

**Why it happens:** Default git on Windows uses `core.autocrlf=true`. Husky hooks have shebangs that need LF.

**How to avoid:**
- Add `.gitattributes`:
  ```
  * text=auto eol=lf
  *.bat text eol=crlf
  *.ps1 text eol=crlf
  ```
- In `package.json` `prepare` script: `"prepare": "husky"` (Husky v9 auto-handles permissions).
- vite-plugin-pwa: ensure `globPatterns` uses forward slashes only.
- CI runs ubuntu-latest (D-08) â€” Windows-specific issues caught only in dev. Document in `README.md`.

**Phase to address:** Plan 1 (Monorepo + Tooling).

### Pitfall 3: Dexie Schema Migration Breaks Pending Mutations

**What goes wrong:** Phase 2 ships with Dexie v2 schema; users with pending mutations from v1 see them dropped or corrupted.

**Why it happens:** Dexie `version().upgrade()` transforms data â€” if mutation_queue stores domain objects rather than HTTP requests, schema bumps break pending writes.

**How to avoid (codified in Pattern 5 above):**
- `mutation_queue` stores **opaque HTTP requests** `{endpoint, method, body}`, never domain objects â†’ survives any schema change.
- Cache tables are read-only mirrors; schema bump = drop + re-fetch (never migrate in place).
- Server UUIDs (never auto-int) so refetch is idempotent.
- Document this contract in `frontend/src/db/dexie.ts` header comment.

**Warning signs:** Sentry "missing key X" after deploy; user reports "lost data after update".

**Phase to address:** Plan 6 (PWA Shell + Dexie) â€” set the rule in code header.

### Pitfall 4: JWT Refresh Race on iOS Resume

**What goes wrong:** PITFALLS.md #4 â€” iPhone resume fires N parallel queries â†’ N concurrent 401s â†’ N concurrent refresh attempts â†’ server detects "reuse" â†’ revokes family â†’ user logged out mid-task.

**How to avoid (codified in Patterns 9):**
- Singleton refresh promise client-side (`refreshTokenAtomic.ts`).
- 10s server-side idempotent grace window in `rotate_refresh()`.
- Pre-emptive refresh: if access token expires in <60s, refresh proactively (decode `exp` claim).
- Test scenario: kill app â†’ wait 16 min â†’ reopen â†’ assert single `/api/auth/refresh` call.

**Phase to address:** Plan 3 (Auth).

### Pitfall 5: MD Parser BOM Trap â€” `utf-8` vs `utf-8-sig`

**What goes wrong:** UploadFile bytes contain BOM (`\xef\xbb\xbf`) prefix. `bytes.decode('utf-8')` returns string starting with `ï»¿`. First heading regex fails because heading is preceded by zero-width-no-break-space.

**How to avoid:** ALWAYS use `'utf-8-sig'` for incoming MD bytes. Test fixture `notepad_bom.md` exists in `backend/tests/fixtures/plans/evil/` to lock this in CI.

**Warning signs:** Parser passes unit tests on synthetic fixtures, fails on real Stefano upload from Notepad.

**Phase to address:** Plan 4 (MD Parser).

### Pitfall 6: OKLCH Browser Baseline (Safari 16.4+)

**What goes wrong:** OKLCH colors invalid in Safari <16.4 â†’ fallback to `currentColor` or invalid â†’ colors render as black/white.

**How to avoid:**
- iOS Web Push (FND-05 stretch / Phase 3 hard) requires Safari 16.4+ already, so baseline aligns.
- Add explicit baseline check in `index.html`:
  ```html
  <script>
    if (!CSS.supports('color', 'oklch(50% 0 0)')) {
      document.documentElement.classList.add('no-oklch');
    }
  </script>
  ```
- Provide fallback via `@supports not (color: oklch(0 0 0))` rule in `globals.css` with HSL fallback for critical brand colors.
- Document Safari 16.4 minimum in `README.md`.

**Phase to address:** Plan 5 (Frontend Skeleton).

### Pitfall 7: Tailwind 4 `@theme` + Dark Mode Manual Override

**What goes wrong:** UI-SPEC Â§4.1 declares dark via both `@media (prefers-color-scheme: dark)` AND manual `data-theme="dark"`. Naive override leaves residual light tokens after toggle.

**How to avoid:**
- Use `:root[data-theme="dark"]` in CSS to mirror ALL dark tokens explicitly (not just selective).
- Settings ThemeToggle writes to `data-theme` attribute on `<html>` and persists in localStorage.
- Tailwind 4 `darkMode` config (in `theme.css`):
  ```css
  @custom-variant dark (&:is([data-theme="dark"] *), &:is(.dark *));
  ```
  enables `dark:bg-...` utilities to respect manual toggle.

**Phase to address:** Plan 5.

### Pitfall 8: Recharts Dark Mode Hardcoded Colors

**What goes wrong:** UI-08 requires Recharts colors via CSS variables. Default Recharts demos use `stroke="#8884d8"` etc. â†’ hardcoded â†’ dark mode broken.

**How to avoid:** Every Recharts component prop uses `var(--color-...)`:

```tsx
<Line stroke="var(--color-neutral-700)" />
<XAxis stroke="var(--color-neutral-500)" />
<Tooltip contentStyle={{ background: 'var(--color-bg-elev)', border: '1px solid var(--color-neutral-200)' }} />
```

Code review checklist must verify: zero hex literals in `components/weight/`.

**Phase to address:** Plan 7 (/today + weight + workout).

### Pitfall 9: Italian Decimal Separator vs Form Validation

**What goes wrong:** User types `75,3` for weight; Zod schema parses as `number` â†’ fails because `Number('75,3') === NaN`.

**How to avoid:**
- Input mask + `inputmode="decimal"` on weight input.
- Zod custom transform: `z.string().transform((s) => Number(s.replace(',', '.'))).pipe(z.number())`.
- Display via `Intl.NumberFormat('it-IT')`.
- Helper `parseItalianDecimal()` in `lib/format.ts`.

**Phase to address:** Plan 7.

### Pitfall 10: WIN REQUISITE Drift â€” Hardcoded Hex During Wave 1

**What goes wrong:** Plan 5 (Frontend Skeleton) lands tokens, but Plan 7 (Today/Weight/Workout) parallel agent forgets to use them â€” ships with `bg-slate-100` etc.

**How to avoid:**
- Plan 5 MUST land BEFORE Plan 7 (sequential, not parallel).
- ESLint rule `no-restricted-syntax` for `style.color/background` with hex.
- Code review checklist: grep for `#[0-9a-fA-F]{3,8}` in PR diff outside theme.css.
- axe-core CI gate catches contrast issues; visual diff catches gross misuse.

**Phase to address:** Plans 5 â†’ 7 strict sequencing.

### Pitfall 11: pnpm Workspace + Backend Outside Workspace

**What goes wrong:** Developer runs `pnpm install` at root expecting to install backend deps. Backend uses uv, not pnpm. Confusion.

**How to avoid:**
- `pnpm-workspace.yaml`:
  ```yaml
  packages:
    - 'frontend'
  ```
- Root `package.json` only contains workspace scripts:
  ```json
  {
    "name": "wellness-buddy",
    "private": true,
    "scripts": {
      "frontend:dev": "pnpm --filter frontend dev",
      "frontend:build": "pnpm --filter frontend build",
      "backend:dev": "cd backend && uv run uvicorn app.main:app --reload",
      "backend:test": "cd backend && uv run pytest",
      "dev": "concurrently \"pnpm frontend:dev\" \"pnpm backend:dev\""
    },
    "devDependencies": { "concurrently": "^9" }
  }
  ```
- Document in `README.md`: "Frontend uses pnpm; backend uses uv. They are separate."

**Phase to address:** Plan 1.

### Pitfall 12: GitHub Actions axe-core CI on Built dist/

**What goes wrong:** axe-core run against `vite dev` server has different bundle than production â†’ inconsistencies. Or run against pre-build â†’ no SW assertions.

**How to avoid:**
- `axe-a11y.yml`: `pnpm build` â†’ `pnpm exec serve dist -l 4173` â†’ Playwright runs against `http://localhost:4173`.
- Document axe-core thresholds in `playwright.config.ts`:
  ```ts
  // Source: UI-10, UI-SPEC Â§9
  use: { contextOptions: { reducedMotion: 'reduce' } },  // also test reduced-motion
  ```

**Phase to address:** Plan 5.

## Code Examples

### Backend `main.py` skeleton

```python
# backend/app/main.py
# Source: ARCHITECTURE.md Â§4 Pattern 2 lifespan, FND-03
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware, IdempotentGraceMiddleware
from app.ai.factory import build_provider
from app.api import auth, plans, today, weight, workout, ai, admin, errors, version

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    app.state.ai_provider = build_provider()
    yield

app = FastAPI(title="Wellness Buddy API", version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(IdempotentGraceMiddleware)

for r in [auth.router, plans.router, today.router, weight.router, workout.router,
          ai.router, admin.router, errors.router, version.router]:
    app.include_router(r)
```

### Frontend `main.tsx` entry

```typescript
// frontend/src/main.tsx
// Source: FND-04, vite-plugin-pwa registration
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router';
import { QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import 'geist/font/sans';
import 'geist/font/mono';
import './styles/theme.css';
import './styles/globals.css';
import { router } from './router';
import { queryClient } from './lib/queryClient';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster position="top-right" richColors closeButton />
    </QueryClientProvider>
  </StrictMode>,
);
```

### Auth login + refresh flow

Already shown in Pattern 9 above.

### Today endpoint (TODAY-01..TODAY-08)

```python
# backend/app/api/today.py
# Source: TODAY-01..TODAY-08
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.services.today_service import build_today_payload

router = APIRouter(prefix="/api/today", tags=["today"])

@router.get("")
async def get_today(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await build_today_payload(session, user)

@router.post("/meal/{meal_type}/complete")
async def complete_meal(
    meal_type: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # mark meal completed in WeeklyPlanVariant for today
    ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind v3 + `tailwind.config.ts` | Tailwind v4 + CSS `@theme` block | Jan 2025 (Oxide) | Configuration moves to CSS, 2-5x faster builds, container queries first-class |
| framer-motion | motion (renamed mid-2025) | mid-2025 | API identical; package name only |
| pip + venv + pip-tools | uv (Astral) | 2024-2026 | Single tool, deterministic lock, 10-100x faster |
| `python-jose` JWT only | python-jose still standard | â€” | No change for HS256 path |
| react-router v6 BrowserRouter | react-router v7 createBrowserRouter | 2024 | Unified data router, loaders/actions |
| Create React App | Vite | 2023+ | CRA deprecated |
| Class-based shadcn (v3 style) | shadcn/ui v4 with `@theme` | 2025 | Native CSS variable consumption |
| Manual fetch + axios interceptors | TanStack Query v5 + native fetch + custom interceptor | 2024+ | Standard 2026 |
| Moment.js | date-fns v4 | 2020+ | Tree-shakable, immutable |
| Inter as default | Geist Sans + Mono | 2024+ for elegant+playful brief | Friendlier apertures |
| react-hot-toast | Sonner | 2024-2025 | Sonner 9.7x lead |

**Deprecated/outdated:**
- CRA (Create React App): use Vite
- `framer-motion` package name: still works as alias but `motion` is canonical
- Tailwind v3 `@apply` heavy custom classes: prefer `@theme` tokens consumed via utility classes
- `psycopg2` sync: use `asyncpg` for SQLAlchemy 2 async
- `pytz`: replaced by stdlib `zoneinfo` (Python 3.9+)
- Pydantic v1 `@validator` / `Config` class: dropped in v2 (use `@field_validator` / `model_config`)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | shadcn/ui v4 CLI honors `components.json` `tailwind.css` pointing to `theme.css` instead of `tailwind.config.ts` | shadcn CLI Install | If wrong, components generated with v3-style imports â€” fixable by manual edit but adds friction. **Mitigation:** Plan 5 first task = `pnpm dlx shadcn@latest init` and verify generated `button.tsx` reads from `@/components/ui/button` and uses CSS variables. [ASSUMED â€” STACK.md states "shadcn/ui has full v4 support" but exact CLI behavior 2026-05 not directly verified] |
| A2 | `pytest-postgresql` ^6.x supports Python 3.12 + ephemeral Docker | Test Infrastructure | If wrong, fall back to `pytest-docker` + manual postgres image. **Mitigation:** Plan 1 includes smoke test in CI. [ASSUMED â€” package exists per STACK.md but version compat 2026-05 not directly verified] |
| A3 | `vite-plugin-pwa` 0.21 produces SW that ignores `index.html` precache when `globPatterns` excludes it | Workbox Config | If wrong, must switch to `injectManifest` strategy. **Mitigation:** Test upgrade path manually (deploy v1 â†’ install on iPhone â†’ deploy v2 â†’ verify update toast). [ASSUMED â€” vite-pwa docs describe the pattern; exact behavior of glob exclusion not directly verified] |
| A4 | `motion` v12 `useReducedMotion()` hook reliably reads `prefers-reduced-motion` and re-renders on change | Motion Config | If wrong, manual media query listener required. **Mitigation:** wrap in `hooks/useReducedMotion.ts` with manual fallback. [ASSUMED] |
| A5 | OKLCH baseline of Safari 16.4+ aligns with iOS Web Push baseline | Browser Baseline | If 5% of users have older Safari, colors break. **Mitigation:** `@supports not (color: oklch())` HSL fallback for critical tokens. [VERIFIED: STACK.md "v4 requires Safari 16.4+ â€” already required by iOS Web Push"] |
| A6 | `python-jose[cryptography]` HS256 + symmetric key sufficient for 2-user family deployment | Auth | If wrong (asymmetric keys for kid sessions), refactor to RS256. **Mitigation:** keep `algorithm` configurable in `core/security.py`. [VERIFIED: AUTH-04/05 + 2-user scope] |
| A7 | Plan MD files Stefano+Marta will be edited primarily on macOS (Notes.app NFD) and Windows (Word CRLF) â€” corpus covers these | MD Parser | If users use exotic editor (e.g., Vim+Linux dotfiles), edge cases emerge. **Mitigation:** evil corpus is extensible; `unrecognized_headings` warned not failed. [ASSUMED â€” based on Stefano/Marta personas, not directly observed] |
| A8 | Stefano accepts Tailwind 4 + OKLCH browser baseline restriction (Safari 16.4+) | Browser Baseline | If existing user has older device, dead. **Mitigation:** confirmed in PROJECT.md / STACK.md decisions. [VERIFIED: STACK.md decision rationale] |
| A9 | `axe-core/playwright` reports contrast violations consistently in CI runner light/dark mode | a11y CI | If reduced-motion or color-scheme not switchable in CI, manual review needed. **Mitigation:** `playwright.config.ts` uses `colorScheme: 'dark'` matrix in dark-mode-screenshot.yml. [ASSUMED] |

**No A-tagged claims block phase planning** â€” all assumptions have documented mitigations and can be verified in Plan 1 smoke tests or Plan 5 first PR.

## Open Questions (RESOLVED)

1. **shadcn/ui CLI exact prompt answers for components.json baseColor**
   - What we know: UI-SPEC Â§4 declares OKLCH neutrals. shadcn baseColor prompt offers neutral/zinc/slate/stone.
   - What's unclear: Does setting baseColor=neutral and then overriding via `@theme` work cleanly?
   - **RESOLVED:** Recommendation: Plan 5 task: run `pnpm dlx shadcn init`, verify generated `theme.css` baseline includes neutral, then PREPEND/REPLACE with our `@theme` block from this RESEARCH.md.

2. **Storyset illustration final selection (D-86 Claude's Discretion)**
   - What we know: UI-SPEC Â§6.2 declares EmptyState component needs Storyset illustration (200Ã—200 mobile / 280Ã—280 desktop).
   - What's unclear: Which specific illustrations from Storyset packs (e.g., "Wellness pack vol. 2" vs "Healthy lifestyle pack")?
   - **RESOLVED:** Recommendation: Plan 8 (Tone Calibration Mockups) task: prepare 4-5 candidate illustrations colorized to brand tokens, present to Stefano+Marta during exit-gate review alongside tone variants.

3. **Lottie animations Sprint 1 (D-89 Claude's Discretion)**
   - What we know: UI-SPEC Â§5 motion budget allows celebration â‰¤800ms. UI-04 says Motion v12 for state transitions.
   - What's unclear: Are any Lottie animations needed in Phase 1 (welcome screen + meal-completion)?
   - **RESOLVED:** Recommendation: Phase 1 ships ZERO Lottie (UI-SPEC Â§5 "Forbidden in Phase 1: Lottie (Phase 3)"). Welcome screen uses Motion v12 spring physics + Storyset hero illustration. Meal-completion = SVG path stroke-dasharray draw 200ms. Phase 3 introduces Lottie. **Locked: no Lottie Phase 1.**

4. **Backend `/version.json` build_hash injection mechanism**
   - What we know: FND-06 requires `/version.json` polling.
   - What's unclear: Backend serves static? Or generated dynamically from env? Frontend reads `import.meta.env.VITE_BUILD_HASH`?
   - **RESOLVED:** Recommendation: Both. Backend: `version.py` serves dict from `settings.APP_VERSION + settings.BUILD_HASH` (env-injected at deploy). Frontend: `vite.config.ts` defines `__BUILD_HASH__` from git SHA at build time. Polled `/version.json` returns backend's; compared against frontend's `import.meta.env.VITE_BUILD_HASH`.

5. **Tone calibration mockups output format (Phase 1 exit gate)**
   - What we know: UI-SPEC Â§8 mandates 3 mockups (75/25, 50/50, 25/75) of `/today` mobile + desktop, light + dark, populated + empty.
   - What's unclear: Figma vs Storybook vs HTML/CSS standalone vs deployed staging?
   - **RESOLVED:** Recommendation: **HTML/CSS standalone** â€” zero Figma dependency, Stefano can open URL on real iPhone (mobile preview), URL deployed via GitHub Pages preview or local Vite. Why: tokens already exist in code (Plan 5), mockups become real renderable code that doubles as Plan 7 starting point.

## Environment Availability

> Phase 1 dev environment audit. Production Windows Server 2019 audit deferred to deploy plan (end of Phase 1).

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js LTS (â‰¥20) | Frontend Vite/pnpm | Verify in Plan 1 | TBD | nvm install 20 |
| pnpm | Frontend deps | Verify | TBD | `npm i -g pnpm` |
| Python 3.12 | Backend | Verify | TBD | pyenv / chocolatey |
| uv (Astral) | Backend deps | Verify | TBD | `pip install uv` first |
| Docker | Dev postgres + CI | Verify | TBD | Required (D-13 forbids sqlite) |
| PostgreSQL client (psql) | Manual `CREATE DATABASE WellnessBuddy` | Verify | TBD | Use Docker exec into container |
| Git | Version control | Assumed yes | TBD | â€” |
| GitHub Actions | CI runners | yes (D-08) | hosted | â€” |

**Plan 1 task:** Add `scripts/check-env.sh` (POSIX) + `scripts/check-env.ps1` (Windows) that verify presence + minimum versions of all the above and print Italian-friendly setup instructions if missing.

**Production environment (Windows Server 2019) â€” verified by Stefano during Plan 8 deploy task:**

| Dependency | Required By | Status | Notes |
|------------|------------|--------|-------|
| PostgreSQL | DB | ALREADY INSTALLED (per CONTEXT.md "Integration Points") | Only `CREATE DATABASE WellnessBuddy;` needed |
| IIS | Reverse proxy | ALREADY CONFIGURED for other epartner.it sites | Add new site |
| URL Rewrite + ARR modules | Reverse proxy `/api/*` â†’ 8000 | Likely present (other sites use it) | Verify; install if missing |
| NSSM | Wrap Uvicorn as Windows service | KNOWN PATTERN (CONTEXT.md) | Stefano familiar |
| win-acme | Let's Encrypt cert | KNOWN PATTERN (CONTEXT.md) | Stefano familiar |
| Python 3.12 (server) | Backend runtime | Verify | Install if missing |
| GTK3 Runtime | WeasyPrint (Phase 2 only) | NOT NEEDED Phase 1 | Defer Phase 2 |

**Missing dependencies with no fallback:** None â€” all required tools either installed or installable.

**Missing dependencies with fallback:** None.

## Validation Architecture

> nyquist_validation enabled per `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Backend framework | pytest 8.x + pytest-asyncio + httpx AsyncClient + pytest-postgresql |
| Frontend framework | Vitest 2.x (unit + component) + Playwright 1.x (e2e + visual) + @axe-core/playwright (a11y) |
| Backend config file | `backend/pyproject.toml` `[tool.pytest.ini_options]` |
| Frontend config files | `frontend/vitest.config.ts` + `frontend/playwright.config.ts` |
| Quick run command (backend) | `cd backend && uv run pytest -x --ff` |
| Quick run command (frontend unit) | `cd frontend && pnpm vitest run` |
| Full suite command (backend) | `cd backend && uv run pytest --cov=app --cov-fail-under=80` |
| Full suite command (frontend) | `cd frontend && pnpm vitest run && pnpm playwright test` |
| Full suite phase gate | `pnpm run ci:all` (root script chaining backend + frontend + axe + visual) |

### Phase Requirements â†’ Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FND-01 | Monorepo lint+typecheck pass | smoke | `pnpm lint && pnpm typecheck` (root) | âŒ Wave 0 |
| FND-02 | Alembic baseline applies cleanly | integration | `cd backend && uv run alembic upgrade head` (CI runs against fresh DB) | âŒ Wave 0 |
| FND-03 | FastAPI app starts + lifespan binds AI provider | integration | `pytest backend/tests/integration/test_app_startup.py -x` | âŒ Wave 0 |
| FND-04 | Frontend builds + Tailwind 4 @theme tokens render | smoke | `pnpm build && pnpm preview` + Playwright assertion | âŒ Wave 0 |
| FND-05 | PWA manifest + SW register on production build | e2e | `pnpm playwright test e2e/pwa.spec.ts -g "manifest"` | âŒ Wave 0 |
| FND-06 | `/version.json` polling triggers update toast on mismatch | e2e | `pnpm playwright test e2e/pwa.spec.ts -g "version-update"` | âŒ Wave 0 |
| FND-07 | Dexie schema v1 opens + tables exist | unit | `pnpm vitest run src/db/dexie.test.ts` | âŒ Wave 0 |
| FND-08 | `navigator.storage.persist()` invoked post-login + Dexie-empty resync | e2e | `pnpm playwright test e2e/auth.spec.ts -g "persist-storage"` | âŒ Wave 0 |
| FND-09 | All UI strings sourced from `copy.it.ts`, no hardcoded literals | unit (custom ESLint rule) | `pnpm lint --rule 'no-restricted-syntax: error'` | âŒ Wave 0 |
| AUTH-01..03 | Login + logout + persist 7 days | integration | `pytest backend/tests/integration/test_auth_api.py::test_login_logout_persist` | âŒ Wave 0 |
| AUTH-04 | Access token in Zustand memory only | unit | `pnpm vitest run stores/auth.test.ts` | âŒ Wave 0 |
| AUTH-05 | Refresh token in HttpOnly+Secure+SameSite=Lax cookie | integration | `pytest backend/tests/integration/test_auth_api.py::test_refresh_cookie_attrs` | âŒ Wave 0 |
| AUTH-06 | Refresh rotation + family revocation on reuse | integration | `pytest backend/tests/integration/test_auth_api.py::test_refresh_rotation_family` | âŒ Wave 0 |
| AUTH-07 | Singleton refresh promise â€” concurrent 401s coalesced | unit | `pnpm vitest run lib/refreshTokenAtomic.test.ts` | âŒ Wave 0 |
| AUTH-08 | 10s grace window idempotent | integration | `pytest backend/tests/integration/test_auth_api.py::test_refresh_grace_window` | âŒ Wave 0 |
| AUTH-09..10 | Invite-only signup + admin generates token | integration | `pytest backend/tests/integration/test_auth_api.py::test_invite_flow` | âŒ Wave 0 |
| AUTH-11 | `/api/auth/me` returns profile | integration | `pytest backend/tests/integration/test_auth_api.py::test_me_endpoint` | âŒ Wave 0 |
| AUTH-12 | API errors all `{detail, code}` JSON | integration | `pytest backend/tests/integration/test_error_format.py` | âŒ Wave 0 |
| MOD-01..10 | All models + indexes + TIMESTAMPTZ | unit | `pytest backend/tests/unit/test_models.py` | âŒ Wave 0 |
| PLAN-01..06 | Parser tolerant + strict + evil corpus passes | unit | `pytest backend/tests/unit/test_plan_parser.py` (corpus iteration) | âŒ Wave 0 |
| PLAN-07..10 | Upload + activate + diff + assign | integration | `pytest backend/tests/integration/test_plans_api.py` | âŒ Wave 0 |
| TODAY-01..08 | /today landing + meal complete + offline | e2e | `pnpm playwright test e2e/today.spec.ts` | âŒ Wave 0 |
| WEIGHT-01..02 | Recharts line + history table | unit + e2e | `pnpm vitest run components/weight/` + `pnpm playwright test e2e/weight.spec.ts` | âŒ Wave 0 |
| WORK-01..02 | Form + history filter | unit + e2e | `pnpm vitest run components/workout/` + `pnpm playwright test e2e/workout.spec.ts` | âŒ Wave 0 |
| AI-01..07 | ABC + NullProvider + DI + 501 + locked widget | integration + unit | `pytest backend/tests/integration/test_ai_api.py` + `pnpm vitest run components/ai/AIWidget.test.tsx` | âŒ Wave 0 |
| DEP-01..05/08/09 | NSSM + IIS + win-acme + Docker compose | manual-only | DEPLOY.md checklist exec by Stefano | âŒ Wave 0 |
| UI-01..09 | Tokens, mobile-first, shadcn customized, motion budget, dark mode, etc. | visual + unit | Playwright visual diff + ESLint custom rule | âŒ Wave 0 |
| UI-10 | axe-core â‰¥4.5:1 / â‰¥3:1 | a11y | `pnpm playwright test e2e/a11y.spec.ts` (axe assertions) | âŒ Wave 0 |
| UI-11 | Lighthouse a11y â‰¥95 | a11y | GitHub Action `lighthouse-ci` | âŒ Wave 0 |
| UI-12 | Dark mode screenshot tests CI | visual | `pnpm playwright test visual/routes.spec.ts --grep dark` | âŒ Wave 0 |
| UI-13 | VoiceOver smoke iOS | manual-only | Phase pause-gate checklist by Stefano | âŒ Wave 0 |
| UI-14..20 | Illustrations a11y, form errors, iOS keyboard, tone, Italian formatting, emoji budget, impeccable | mixed | per-component checks + manual review | âŒ Wave 0 |

### Sampling Rate

- **Per task commit:** Husky pre-commit runs `pnpm lint --staged && pnpm typecheck` (frontend) + `uv run ruff check && uv run mypy app` (backend) + relevant unit tests for changed files (lint-staged config).
- **Per wave merge:** Run quick suite both stacks: `pnpm vitest run + pnpm playwright test --grep @smoke + uv run pytest -x`.
- **Phase gate:** Full suite `pnpm run ci:all` green + axe-core green + Lighthouse 95+ + dark-mode screenshot diff zero regressions + manual VoiceOver smoke + manual real-iPhone install + tone calibration mockups signed by Stefano+Marta.

### Wave 0 Gaps

All test infrastructure absent (greenfield). Wave 0 must establish:

- [ ] `backend/pyproject.toml` with `[tool.pytest.ini_options]` + `[tool.ruff]` + `[tool.mypy]`
- [ ] `backend/tests/conftest.py` with pytest-postgresql ephemeral fixture, async client fixture, factory fixtures for User/Plan
- [ ] `backend/tests/fixtures/plans/valid/` and `evil/` corpus
- [ ] `frontend/vitest.config.ts` (jsdom environment)
- [ ] `frontend/playwright.config.ts` (axe-core integration, projects for chromium + chromium-dark + iphone-15)
- [ ] `frontend/tests/e2e/` smoke tests
- [ ] `frontend/tests/visual/routes.spec.ts` for dark-mode diff
- [ ] `.github/workflows/pr.yml` (lint + typecheck + unit + build, both stacks, both ubuntu-latest)
- [ ] `.github/workflows/axe-a11y.yml` (Playwright + axe against `pnpm preview`)
- [ ] `.github/workflows/dark-mode-screenshot.yml` (visual diff)
- [ ] Husky `.husky/pre-commit` + `lint-staged.config.js`
- [ ] Custom ESLint rule for `no-hardcoded-hex-outside-theme` (or rely on grep CI step)
- [ ] Lighthouse CI config + baseline `lighthouserc.json` with a11y â‰¥95 + PWA = 100

**Wave 0 plan owner:** Plan 1 (Monorepo + Tooling) lands all CI infra + test scaffolding before any feature plan.

## Security Domain

> security_enforcement enabled (absent = enabled per default).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | python-jose HS256 + passlib bcrypt rounds=12 + invite-only signup + 24h single-use revocable invite tokens |
| V3 Session Management | yes | JWT access 15min in-mem + refresh 7d HttpOnly+Secure+SameSite=Lax + rotation + family revocation + 10s idempotent grace |
| V4 Access Control | yes Phase 1 (single-tenant); Phase 2 + Phase 4 add multi-user + RLS | `Depends(get_current_user)` on every protected endpoint; `Depends(require_admin)` on admin |
| V5 Input Validation | yes | Pydantic v2 strict schemas at API boundary; Zod on frontend; MD parser tolerantâ†’strict split |
| V6 Cryptography | yes | python-jose for JWT (no custom crypto); passlib bcrypt for passwords (no custom hash); HTTPS via win-acme |
| V7 Error Handling & Logging | yes | structlog JSON; Italian copy via `copy.it.ts` `code` lookup; mask `password`, `Authorization`, `cookie` headers |
| V8 Data Protection | yes | `.env` gitignored, DPAPI on Windows; SECRET_KEY 32-byte token_hex; HttpOnly cookie; UUID server-generated |
| V9 Communications | yes | HTTPS enforced via win-acme + IIS termination; CORS strict allowlist via `CORS_ORIGINS` env, validated at boot |
| V10 Malicious Code | yes (deferred Phase 5 prompt-injection) | Phase 1: limit MD upload to 1 MB; sanitize re-displayed parsed content via `react-markdown` (no `dangerouslySetInnerHTML`) |
| V11 Business Logic | yes | partial unique index `WHERE is_active = true` ensures only one active plan per user |
| V12 File & Resources | yes | UploadFile `.md` only + size cap; stored outside web-served path; served via auth-checked endpoint |
| V13 API & Web Service | yes | OpenAPI auto-generated; rate limiting deferred Phase 5 (AI cost cap); admin endpoints behind `require_admin` |
| V14 Configuration | yes | Pydantic settings BaseSettings reads `.env`; `SECRET_KEY` validated at boot, fail-fast if missing |

### Known Threat Patterns for FastAPI + React PWA + PostgreSQL

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection | Tampering | SQLAlchemy parameterized everything; ban `text()` with f-strings via lint rule |
| XSS via plan MD content | Tampering / Information disclosure | `react-markdown` (safe by default), sanitize via remark plugins; never `dangerouslySetInnerHTML` |
| CSRF on cookie-auth POST | Spoofing | `SameSite=Lax` on refresh cookie + access token in Authorization header (not cookie) â†’ CSRF surface = `/api/auth/refresh` only, which is idempotent and safe |
| JWT theft via XSS | Spoofing | Refresh in HttpOnly cookie; access in memory (Zustand) â€” XSS cannot steal refresh, can only steal short-lived access |
| JWT replay after logout | Spoofing | Logout endpoint revokes refresh family server-side; access expires in 15min |
| JWT refresh race storm (iOS resume) | DoS / repudiation | Singleton refresh promise + 10s grace window |
| Mass account enumeration | Information disclosure | Login error message identical for invalid email vs invalid password ("Email o password non corretti") |
| Brute force login | DoS | Rate limit on `/api/auth/login` (deferred Phase 5; Phase 1 exposed endpoint with strong bcrypt rounds=12 acceptable for 100-user scope) |
| Invite token brute force | Spoofing | 24h expiry, single-use, secure random 32-byte token, revocable |
| File upload abuse | DoS | 1 MB cap on `.md` upload; reject non-`.md` MIME; hash-based duplicate detection |
| Path traversal in plan storage | Information disclosure | Store plans by UUID, never user-supplied filename |
| Sensitive data in logs | Information disclosure | structlog processor masks `password`, `Authorization`, `cookie` keys |
| Stored MD with crafted content | Tampering | Strict Pydantic v2 validation downstream of tolerant parser; reject malformed `parsed_json` shape |
| AI prompt injection (Phase 5) | Tampering | OUT OF SCOPE Phase 1 â€” Phase 5 first PR introduces `<user_note>` delimiters + output validation |
| CORS wildcard leak | Information disclosure | `allow_origins=settings.CORS_ORIGINS` â€” strict allowlist validated at boot, fail-fast if `*` in production |
| Dependency vulnerabilities | Supply chain | `pnpm audit` + `uv pip audit` in CI weekly; Dependabot enabled |

### Phase 1 Specific Security Tasks

- [ ] `SECRET_KEY` generation script in DEPLOY.md
- [ ] HttpOnly cookie attrs explicitly tested in `test_refresh_cookie_attrs`
- [ ] Negative authz test: User A cannot read User B's `/api/today` (Phase 1 single-user but plumbing tested)
- [ ] Login rate-limit deferred Phase 5 (acknowledged risk for 100-user scope)
- [ ] Audit log writes for User/Group/NutritionPlan create/update/delete (D-23)
- [ ] `.env.example` files contain only placeholders, never real values
- [ ] CI grep step: fail PR if `*.env` or `*secret*` files committed (use `pre-commit-secrets` or `gitleaks`)

## Sources

### Primary (HIGH confidence)

- `.planning/research/STACK.md` â€” Stack picks + version pins, verified 2026-05-01
- `.planning/research/ARCHITECTURE.md` â€” System architecture + DI patterns + DB pool config
- `.planning/research/PITFALLS.md` â€” 12 pitfalls with mitigations (#1-12)
- `.planning/research/SUMMARY.md` â€” Cross-cutting themes + Sprint 1 must-haves
- `.planning/phases/01-foundation/01-UI-SPEC.md` â€” Design contract APPROVED 6/6
- `.planning/phases/01-foundation/01-CONTEXT.md` â€” 33 user decisions D-01 through D-33
- `.planning/REQUIREMENTS.md` â€” Phase 1 REQ-IDs locked
- `CLAUDE.md` â€” Project conventions

### Secondary (MEDIUM confidence)

- shadcn/ui v4 CLI (`pnpm dlx shadcn@latest init`) â€” exact prompt behavior 2026-05 inferred from STACK.md "shadcn/ui has full v4 support"
- vite-plugin-pwa 0.21 `globPatterns` exclusion of index.html â€” pattern from upstream docs, exact behavior assumed (A3)
- pytest-postgresql ^6.x Python 3.12 compat â€” assumed (A2)
- Tailwind 4 `@custom-variant dark` syntax for manual data-theme override â€” Tailwind 4 docs

### Tertiary (LOW confidence)

- None â€” all critical claims either verified via upstream research or marked `[ASSUMED]` with mitigation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH â€” versions verified in STACK.md 2026-05-01, browser baseline aligned with iOS Web Push requirement
- Architecture: HIGH â€” patterns verified across STACK.md + ARCHITECTURE.md + PITFALLS.md cross-reference
- Pitfalls: HIGH â€” 12 pitfalls already cataloged in PITFALLS.md; this RESEARCH adds 12 Phase-1-specific 2026 traps
- Tone calibration: MEDIUM â€” output format recommendation (HTML/CSS standalone) is Claude's reasoned suggestion, awaits Stefano+Marta confirmation at exit gate
- shadcn/ui CLI exact behavior: MEDIUM (A1) â€” flagged for Plan 5 first-task verification
- Test infrastructure: HIGH â€” patterns standard 2026 (pytest-postgresql, Playwright + axe, Vitest + jsdom)

**Research date:** 2026-05-01
**Valid until:** 2026-06-01 (30 days â€” stack stable, no major Tailwind 4 / Vite 7 / FastAPI / shadcn breaking changes expected)

---
*Phase 1 Foundation research completed: 2026-05-01*
