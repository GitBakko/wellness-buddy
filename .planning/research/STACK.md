# Stack Research — Wellness Buddy PWA

**Domain:** Self-hosted nutrition tracking PWA (mobile-first, offline-first, multi-user, AI-pluggable)
**Researched:** 2026-05-01
**Overall confidence:** HIGH

---

## Executive Validation Summary

The contract-pinned stack (React 19, Vite 7, TailwindCSS 3, Zustand, TanStack Query v5, Dexie.js v4, FastAPI, SQLAlchemy 2, PostgreSQL, JWT, Alembic) is **largely correct for 2026 — but two version pins need attention** before Sprint 1 starts:

| Pin | Verdict | Action |
|-----|---------|--------|
| **React 19** | VALID — current is 19.2.5 | Use `^19.2` |
| **Vite 7** | VALID but trailing — Vite 8 is stable since March 2026 | KEEP Vite 7.x for the project; Vite 8's Rolldown bundler still maturing for plugin ecosystem. Re-evaluate at Sprint 4. |
| **TailwindCSS 3** | OUTDATED for greenfield — v4 is the 2026 default | RECOMMEND UPGRADE to Tailwind v4 (Oxide engine, 2-5x faster builds, CSS-first config). The contract pin should be revised. |
| **Zustand** | VALID — v5 is current and React 19 compatible | Use `^5.0` |
| **TanStack Query v5** | VALID — current major | Use `^5.x` |
| **Dexie.js v4** | VALID — 4.4.2 latest | Use `^4.4` |
| **FastAPI** | VALID — 0.136.1 current (April 2026) | Use `^0.136` |
| **SQLAlchemy 2** | VALID — async-native | Use `^2.0` |
| **PostgreSQL** | VALID — already installed | n/a |
| **JWT/bcrypt** | VALID — standard pattern | Use `python-jose` + `passlib[bcrypt]` |
| **Alembic** | VALID — standard | Use latest `^1.x` |

**Critical recommendation:** Move from Tailwind 3 to Tailwind 4. The Win Requisite (elite UI/UX) is materially advanced by v4's container queries, 3D transforms, native CSS variables in `@theme`, and shadcn/ui's first-class v4 integration. Sticking with v3 leaves design quality on the table.

---

## Recommended Stack

### Core Frontend

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| React | `^19.2.5` | UI framework | Current stable; React 19 server actions, ref-as-prop, useActionState all relevant. PWA + family-sync use case is well-served. | HIGH (verified npm/react.dev) |
| Vite | `^7.0` | Build tool | Stable, plugin ecosystem mature. Vite 8 (March 2026) ships Rolldown but Sprint 1 stability outweighs marginal build-speed gains. | HIGH (vite.dev) |
| TailwindCSS | **`^4.0`** (override contract pin) | CSS engine | Oxide engine 2-5x faster, container queries critical for responsive meal cards, CSS-first `@theme` config aligns with design-token approach. shadcn/ui has full v4 support. | HIGH (tailwindcss.com) |
| TypeScript | `^5.6` | Type safety | Standard. Required for safe Zod inference, RHF + shadcn integration, Dexie schema typing. | HIGH |

### Core Backend

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Python | `3.12.x` | Runtime | Contract pin. FastAPI 0.130+ requires 3.10+; 3.12 is the recommended target for performance. | HIGH |
| FastAPI | `^0.136.1` | Web framework | Current April 2026 release. Async-native, Pydantic v2 default, OpenAPI docs auto-generated. | HIGH (fastapi.tiangolo.com) |
| SQLAlchemy | `^2.0` | ORM | 2.0 async API (`AsyncSession`, `async_sessionmaker`) is the canonical 2026 pattern with FastAPI. | HIGH |
| Pydantic | `^2.7` | Validation | Required by FastAPI 0.136; Rust-backed core 5-50x faster than v1. | HIGH |
| asyncpg | `^0.29` | PostgreSQL async driver | Required for SQLAlchemy 2.0 async + PostgreSQL. Faster than psycopg async. | HIGH |
| Alembic | `^1.13` | DB migrations | Standard. Contract mandates Alembic-only schema changes. | HIGH |
| Uvicorn | `^0.30` | ASGI server | Standard FastAPI server. Run via NSSM as Windows service. | HIGH |
| python-jose[cryptography] | `^3.3` | JWT | Standard JWT lib, plays well with FastAPI's `OAuth2PasswordBearer`. | HIGH |
| passlib[bcrypt] | `^1.7` | Password hashing | Standard bcrypt wrapper. | HIGH |
| python-multipart | `^0.0.9` | File upload | Required for `.md` plan upload endpoint. | HIGH |

---

### Frontend State, Data, Offline

| Library | Version | Purpose | When/Why to Use | Confidence |
|---------|---------|---------|-----------------|------------|
| Zustand | `^5.0` | Client state | UI state (selected variant, modal open, theme), auth tokens. Tiny (~1KB), no boilerplate, React 19 compatible. | HIGH |
| TanStack Query | `^5.x` | Server state | All API calls — caching, refetch, optimistic updates, mutation. Pairs with Dexie via `persistQueryClient`. | HIGH |
| Dexie.js | `^4.4` | IndexedDB wrapper | Offline cache for plans, weekly variants, weight/workout logs. `useLiveQuery` reactive hook. Sync via mutation queue replayed on reconnect. | HIGH (dexie.org, npm) |
| @tanstack/query-sync-storage-persister | latest | Persist Query cache | Cache survives reload — critical for offline-first feel. | MEDIUM |
| Axios or native fetch | n/a | HTTP client | Native `fetch` + small wrapper is sufficient for 2026; no Axios needed unless interceptor patterns become heavy. | MEDIUM |

### Frontend Routing & PWA

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| react-router | `^7.x` | Routing | De-facto standard. v7 unified data router. | HIGH |
| vite-plugin-pwa | `^0.21` | PWA manifest + SW | Zero-config Workbox 7 integration. `injectManifest` strategy for full SW control. | HIGH |
| workbox-window | `^7.x` | SW lifecycle | Used by vite-plugin-pwa to communicate with SW from the page. | HIGH |
| web-push (backend) | `pywebpush` `^2.0` | VAPID push | Backend send. Generate VAPID keys once, store private in `.env`. iOS Safari 16.4+ supports push for installed PWAs. | HIGH |

---

### UI/UX Stack — Elite Elegant + Playful (WIN REQUISITE)

This section is the most important. The Win Requisite ("elegant/minimal + playful/friendly hybrid, ELITE quality") is materially achievable only with the right composition. The architecture is **layered**:

```
┌─────────────────────────────────────────────────┐
│  LAYER 4 — Delight (Lottie/Rive, custom illos)  │
├─────────────────────────────────────────────────┤
│  LAYER 3 — Motion (Motion/Framer Motion)        │
├─────────────────────────────────────────────────┤
│  LAYER 2 — Components (shadcn/ui + Radix)       │
├─────────────────────────────────────────────────┤
│  LAYER 1 — Primitives (Tailwind v4 + tokens)    │
└─────────────────────────────────────────────────┘
```

#### Component Library

| Library | Version | Purpose | Why for THIS project | Confidence |
|---------|---------|---------|----------------------|------------|
| **shadcn/ui** | latest (CLI-managed) | Component primitives | The 2026 default. Copy-paste model = full ownership of component code, no version lock-in. Built on Radix UI (WAI-ARIA compliant). Tailwind v4 native. Critical for elegance. | HIGH (ui.shadcn.com) |
| **Radix UI primitives** | `^1.x` per primitive | Headless accessibility | Underpins shadcn/ui — Dialog, Popover, DropdownMenu, Tabs, Toggle, Toast. Keyboard nav + ARIA out of the box. | HIGH |
| class-variance-authority (cva) | `^0.7` | Variant API | Build `MealCard variant="optionA" state="completed"` cleanly. Standard in shadcn/ui. | HIGH |
| tailwind-merge | `^2.x` | Class conflict resolution | Pair with cva and clsx. Standard `cn()` utility pattern. | HIGH |
| clsx | `^2.x` | Conditional classes | Tiny, used in every shadcn project. | HIGH |

#### Animation & Motion (the "playful" half)

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **motion** (formerly framer-motion) | `^12.x` | Component animation, gestures | THE choice. Hybrid native/JS engine, 120fps, spring physics, layout animations, gesture handling. 30M monthly downloads. Use `motion/react`. Renamed from framer-motion mid-2025; API identical. | HIGH (motion.dev) |
| **lottie-react** OR **@rive-app/react-canvas** | latest | Hero illustrations, empty states, success moments | LOTTIE if pulling from LottieFiles community packs (faster ship). RIVE if you want true interactive state machines (weight goal celebration, workout streak fire icon). **Recommendation: start with Lottie, add Rive in Sprint 3 for `progress` page hero.** | HIGH (callstack.com, rive.app) |
| **tailwindcss-animate** | `^1.x` | Tailwind animation utilities | Pre-built keyframes used by shadcn/ui (accordion-down, fade-in). | HIGH |

#### Iconography

| Library | Version | Purpose | Why over alternatives | Confidence |
|---------|---------|---------|----------------------|------------|
| **lucide-react** | `^0.460+` | Primary icon set | 16x more popular than Phosphor in 2026. ~1600 stroke-based icons. Tree-shakable. Friendly clean line style fits "elegant + soft". Default in shadcn/ui. | HIGH (wmtips.com, mighil.com) |
| @phosphor-icons/react | optional | Multi-weight icons | Use ONLY if specific multi-weight needs arise (e.g., duotone variant for a hero context). Don't mix everywhere — Phosphor's bundle/runtime overhead is higher. | MEDIUM |

#### Typography

| Font | Role | Why | Confidence |
|------|------|-----|------------|
| **Geist Sans** (Vercel) | Primary UI font | Geometric sans, friendlier apertures than Inter, slightly rounder — **maps perfectly to "elegant + playful" hybrid**. Free, npm-installable (`geist`), variable weight. | HIGH (vercel.com/font, fonts.google.com) |
| **Geist Mono** | Numbers, KPI, weight values | Matches Geist Sans visually; tabular numbers ideal for KPI cards and weight charts. | HIGH |
| Instrument Serif (optional) | Accent display headings on `/today` hero | Editorial elegant counterpoint — use sparingly (one heading per page max) to add "personality without heaviness". | MEDIUM |

**Anti-pattern:** Using Inter as the primary. Inter is excellent but ubiquitous and reads as "neutral SaaS". Geist gives the same legibility with more character — directly serving the playful side of the brief.

#### Illustration Strategy

**Recommendation: Storyset OR Open Doodles for system illustrations + commissioned/AI-generated mascot character for emotional moments.**

| Source | Use For | Notes |
|--------|---------|-------|
| Storyset (storyset.com) | Empty states, onboarding, error pages | Animated SVG export, customizable colors per design token, has "wellness" / "fitness" packs |
| Open Doodles (opendoodles.com) | Playful spot illustrations | Hand-drawn feel, free, 100% customizable |
| LottieFiles (Free packs) | Loading states, success animations, streak fire | Filter by "outline" or "minimal" to keep elegance |
| Custom mascot (Sprint 3+) | Brand character (e.g., a friendly avocado, a measuring-tape ribbon mascot) | Generate via Recraft/Figma + handoff. Single character, three poses (cheering, neutral, snoozing). Used for streak/milestone moments. |

**Anti-pattern:** unDraw monochrome blue style — too SaaS-generic, kills the playful intent. Use only as last-resort placeholder.

#### Forms & Validation

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| react-hook-form | `^7.53` | Form state | 12M weekly downloads; minimal re-renders; shadcn/ui Form component uses it natively. | HIGH |
| zod | `^3.23` | Schema validation | End-to-end type-safe forms; share schemas client/server (parse JSON from FastAPI on client). | HIGH |
| @hookform/resolvers | `^3.9` | RHF + Zod bridge | `zodResolver(schema)`. Standard. | HIGH |

#### Toast / Notifications

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **sonner** | `^1.7` | Toast notifications | 47M weekly downloads, 9.7x lead over react-hot-toast. Tiny (~9KB gzip). Beautiful default styling. Imperative API (`toast.success()`) callable from anywhere. shadcn/ui ships it as the default. | HIGH |

#### Charts (CRITICAL — Weight Projection Chart Decision)

**Decision: Recharts 3.x as primary, with custom Motion-animated overlays for the "delight" layer.**

| Library | Version | Purpose | Why over alternatives | Confidence |
|---------|---------|---------|----------------------|------------|
| **recharts** | `^3.0` | Weight chart, KPI mini-charts, workout time series | 2.4M weekly downloads. Declarative JSX (`<LineChart><Line /></LineChart>`). Easy to compose: real points + projected curve + tolerance band ReferenceArea. Contract already names `WeightChart` as Recharts. SVG renders crisp on iPhone. Can be styled with Tailwind tokens. | HIGH (pkgpulse.com, querio.ai) |
| (alternative) Tremor | not used | — | Tremor is Recharts wrapped in a SaaS-dashboard look. We want bespoke playful style, not generic SaaS — using raw Recharts gives more control. | HIGH |
| (alternative) visx | not used | — | Power-user D3 toolkit; 2-3x build time. Overkill for our chart needs (only 3-4 chart types). | HIGH |

**Recharts pattern for weight chart:**
- `<Line>` for actual weight (real points, dot=true, animated)
- `<Line strokeDasharray="4 4">` for projection curve
- `<ReferenceArea>` for ±0.5kg/wk tolerance band (low opacity)
- Custom tooltip animated with motion
- Empty state replaced with Storyset illustration

#### Dates

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| date-fns | `^4.x` | Date math, week boundaries, formatting | Tree-shakable functional API. v4 has first-class timezone support. Ideal for weekly plan navigation (`startOfWeek({ weekStartsOn: 1 })` for Monday-start). | HIGH |
| react-day-picker | `^9.x` | Calendar component (workout monthly history, week picker) | Headless, WCAG 2.1 AA, Tailwind-styleable. Pairs with shadcn/ui's `<Calendar>` wrapper. | HIGH |

#### Markdown (for plan parsing UI preview & diff view)

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| react-markdown | `^9.x` | Render parsed plan preview, diff view | Safe (no `dangerouslySetInnerHTML`), customizable with React components for tables/headings. Backend does the structured parsing — frontend uses this only for plan preview rendering. | HIGH |
| remark-gfm | `^4.x` | GitHub-flavored markdown plugin | Tables, strikethrough, autolinks — needed for the plan tables. | HIGH |

---

### Backend Supporting Libraries

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **WeasyPrint** | `^62.x` | PDF export of shopping list | **WINS over ReportLab** for THIS project — see decision below. | HIGH (decision rationale below) |
| markdown (Python-Markdown) | `^3.7` | Plan MD → HTML | Standard library. Custom regex parser handles structured sections per contract §8. | HIGH |
| pywebpush | `^2.0` | VAPID push send | Standard Python web-push library. Used in `/api/notifications/test` and Monday-morning cron. | HIGH |
| python-dotenv | `^1.0` | `.env` loading | Standard. | HIGH |
| httpx | `^0.27` | Async HTTP for AI providers | Used by `OllamaProvider`/`OpenAIProvider`/`AnthropicProvider`. Async-native. | HIGH |
| pytest | `^8.x` | Tests | Standard. | HIGH |
| pytest-asyncio | `^0.24` | Async test support | Required for FastAPI/SQLAlchemy async tests. | HIGH |

#### PDF Library Decision: WeasyPrint vs ReportLab

**DECISION: WeasyPrint** (despite Stefano's familiarity with ReportLab).

**Rationale:**

| Criterion | ReportLab | WeasyPrint | Winner |
|-----------|-----------|-----------|--------|
| Layout approach | Imperative canvas (draw each element by coords) | HTML + CSS to PDF | WeasyPrint |
| Shopping list use case | Table by category, checkboxes, branded header | Maps 1:1 to existing component CSS | WeasyPrint |
| Designer iteration | Code change per layout tweak | CSS change | WeasyPrint |
| Brand consistency | Manual font/color reproduction | Reuses Tailwind tokens via shared CSS variables | WeasyPrint |
| Pure Python install | YES | Requires Pango, Cairo, GDK-PixBuf | ReportLab |
| **Windows Server 2019** | Easy (pip only) | **Possible but requires GTK Runtime on Windows** | **ReportLab favorable** |

**Tiebreaker:** The shopping list PDF must look polished (Win Requisite extends to PDF — printed Sunday-night fridge list is a *touchpoint*). Imperative canvas drawing in ReportLab will make styling tedious, encourage cutting corners, and produce a PDF that feels "office print" rather than "loving home brand". WeasyPrint's CSS reuse pays dividends across the project.

**Mitigation for the install pain:** Document the GTK3 Runtime install once in `DEPLOY.md` (single MSI: `gtk3-runtime-3.24.x-msvc.exe`). One-time cost. Stefano accepted similar setup with win-acme/NSSM already.

**Fallback condition:** If Windows GTK install proves unstable in production after Sprint 1 spike, fall back to ReportLab with a Jinja-driven layout helper. Document this as a contingency in PITFALLS.md.

Sources: [Top 10 Python PDF generators 2026](https://www.nutrient.io/blog/top-10-ways-to-generate-pdfs-in-python/), [WeasyPrint Python docs](https://www.codingeasypeasy.com/blog/flask-pdf-generation-reportlab-weasyprint-and-pdfkit-compared), [WeasyPrint vs ReportLab — Kraft issue tracker](https://github.com/dragotin/kraft/issues/62)

---

### Development Tools

| Tool | Purpose | Configuration Notes |
|------|---------|---------------------|
| Vitest `^2.x` | Frontend unit tests | Built-in to Vite ecosystem. Use `@testing-library/react`. |
| Playwright `^1.x` | E2E (smoke for Sprint 1) | Test PWA install + offline mode on Chromium. iOS-Safari real-device QA manual. |
| ESLint `^9` (flat config) | Linting | `eslint-config-react-app` deprecated; use `eslint-plugin-react`, `eslint-plugin-react-hooks`. |
| Prettier `^3` | Formatting | Config integrates with Tailwind class sort plugin. |
| `prettier-plugin-tailwindcss` | Tailwind class sorting | Must-have for consistency. |
| Storybook `^8.x` (optional Sprint 2+) | Component playground | Skip Sprint 1; introduce when shadcn component count >15 and design polish work begins. |
| ruff (Python) | Lint + format | Replaces flake8 + black + isort. 100x faster, single config. |
| mypy `^1.x` | Type checking backend | Strict mode on `app/` subdirs. |
| NSSM | Windows service manager | Already familiar to Stefano. Wrap `uvicorn app.main:app --host 127.0.0.1 --port 8000`. |
| win-acme | Let's Encrypt cert | Already familiar to Stefano. |

---

## Installation Snapshot

```bash
# Frontend ----------------------------------------------------------
cd frontend
npm create vite@latest . -- --template react-ts

# Core
npm install react@^19.2 react-dom@^19.2 react-router@^7
npm install zustand@^5 @tanstack/react-query@^5 @tanstack/react-query-persist-client
npm install @tanstack/query-sync-storage-persister
npm install dexie@^4.4

# UI / Design system
npm install -D tailwindcss@^4 @tailwindcss/vite postcss autoprefixer
npm install class-variance-authority clsx tailwind-merge tailwindcss-animate
npm install lucide-react geist
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu \
            @radix-ui/react-popover @radix-ui/react-tabs @radix-ui/react-toggle \
            @radix-ui/react-toast @radix-ui/react-select @radix-ui/react-checkbox

# Animation & illustrations
npm install motion lottie-react
# Add @rive-app/react-canvas in Sprint 3

# Forms
npm install react-hook-form zod @hookform/resolvers

# Notifications
npm install sonner

# Charts & dates
npm install recharts@^3 date-fns@^4 react-day-picker@^9

# Markdown
npm install react-markdown remark-gfm

# PWA
npm install -D vite-plugin-pwa workbox-window

# Dev
npm install -D vitest @testing-library/react @testing-library/jest-dom \
              @testing-library/user-event jsdom \
              @playwright/test \
              prettier prettier-plugin-tailwindcss \
              eslint @eslint/js typescript-eslint eslint-plugin-react eslint-plugin-react-hooks

# Initialize shadcn/ui CLI
npx shadcn@latest init
# Add components as needed:
npx shadcn@latest add button card dialog dropdown-menu form input \
                       label select tabs toast toggle calendar checkbox

# Backend ----------------------------------------------------------
cd ../backend
python -m venv .venv
.venv\Scripts\activate

pip install "fastapi[standard]>=0.136"
pip install "uvicorn[standard]>=0.30"
pip install "sqlalchemy[asyncio]>=2.0" asyncpg alembic
pip install "pydantic>=2.7" "pydantic-settings>=2.0"
pip install "python-jose[cryptography]>=3.3" "passlib[bcrypt]>=1.7"
pip install python-multipart python-dotenv
pip install markdown
pip install weasyprint  # NOTE: requires GTK3 runtime on Windows
pip install pywebpush
pip install httpx       # for AI providers
pip install -D pytest pytest-asyncio ruff mypy
```

---

## Alternatives Considered

| Recommended | Alternative | When Alternative Wins |
|-------------|-------------|----------------------|
| Tailwind v4 | Tailwind v3 | If supporting Safari <16.4 / Chrome <111 / Firefox <128 (we don't — iOS PWA spec already requires Safari 16.4+). |
| Recharts | Tremor | If we wanted SaaS-default look with no theming work. We want bespoke. |
| Recharts | visx | If we needed exotic chart types (sankey, force-directed, treemap). We have line + bar + KPI mini. |
| Motion | GSAP | If primarily marketing-style scroll animations. We need component/gesture animations + spring physics. |
| Sonner | react-hot-toast | If app is React 17 or pre-shadcn ecosystem. |
| WeasyPrint | ReportLab | If Windows GTK runtime install becomes blocker; or for highly programmatic charts-in-PDF (we only need a styled HTML table). |
| date-fns | Day.js | If migrating from Moment.js / minimum bundle is critical. We're greenfield. |
| date-fns | Temporal API | When polyfill cost (~60KB) drops or browser support reaches 95%. Re-evaluate Q4 2026. |
| Lucide | Phosphor | When project needs duotone or multiple weights of same icon for hierarchy. We can add Phosphor surgically if needed. |
| Geist | Inter | If client/brand specifically demands the maximum-neutral SaaS look. We want personality. |
| shadcn/ui | Mantine / Chakra / MUI | If team prefers all-in-one packaged library over copy-paste ownership. shadcn ownership pays off massively for elite-polish projects. |
| react-hook-form | TanStack Form | If TypeScript inference at field level is a top priority and the team can absorb the smaller ecosystem. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **CRA (Create React App)** | Deprecated since 2023. | Vite |
| **Redux + RTK** for this app | Way over-engineered for 2 users / 100 max with TanStack Query handling server state. | Zustand + TanStack Query |
| **localStorage for plan/log data** | Not transactional, 5MB limit, sync, blocks main thread. | IndexedDB via Dexie |
| **Moment.js** | Deprecated since 2020, mutable API, 70KB. | date-fns v4 |
| **Axios for our scale** | Adds 14KB for features we don't need. | Native fetch with thin wrapper |
| **MUI / Material-UI** | Heavy bundle, opinionated Material aesthetic clashes with playful brief, theming is a fight. | shadcn/ui + Tailwind |
| **Bootstrap / react-bootstrap** | Outdated paradigm, 2026 React doesn't pair well with class-based component systems. | Tailwind + shadcn/ui |
| **Chart.js with react-chartjs-2** | Canvas (no SVG sharpness on Retina), imperative config, harder to animate via Motion. | Recharts |
| **chartjs-plugin-zoom etc.** | We don't need zoom/pan for simple weekly weight chart. | Just Recharts. |
| **ant-design (antd)** | Aesthetics tied to Chinese enterprise SaaS, hard to make playful. | shadcn/ui |
| **NextAuth / Auth.js** | Overkill for invite-only 100-user app. Adds complexity without value when we already do JWT issuance backend-side. | Custom JWT (per contract) |
| **Prisma** (frontend or considered for backend) | We're Python backend. SQLAlchemy 2 async is the canonical FastAPI partner. | SQLAlchemy 2 |
| **Django** | Adds a templating engine and admin we don't need; FastAPI is async-first and already pinned. | FastAPI |
| **Flask** | Sync-first, no built-in OpenAPI/validation, no async story. | FastAPI |
| **Pydantic v1 syntax** (`@validator`, `Config` class) | Removed in v2; FastAPI 0.119+ requires v2. | Pydantic v2 (`@field_validator`, `model_config`) |
| **wkhtmltopdf** | Project is in maintenance / abandoned, security concerns. | WeasyPrint |
| **Sass/SCSS** | Tailwind v4 + CSS variables make Sass redundant. | Tailwind v4 `@theme` |
| **styled-components / Emotion** | Runtime CSS-in-JS conflicts with Tailwind philosophy and adds bundle weight. | Tailwind utility classes + cva |
| **Vite 8** for Sprint 1 | Released March 2026 — Rolldown bundler still settling, plugin compat surprises possible. | Vite 7 now; reassess Sprint 4. |

---

## Stack Patterns by Variant

### When deploying to production (Windows Server 2019)

- Uvicorn `--workers 1` (NSSM service single instance — 100 users doesn't need horizontal scaling)
- IIS reverse proxy via `URL Rewrite` + `Application Request Routing` modules → `http://127.0.0.1:8000`
- Static `dist/` served by IIS as a separate site, with rewrite rules forwarding `/api/*` to Uvicorn
- HTTPS termination at IIS (win-acme cert), backend listens on HTTP loopback

### When developing on Windows

- `npm run dev` → Vite dev server on port 5173 with proxy `/api → http://localhost:8000`
- `uvicorn app.main:app --reload --port 8000` in another terminal
- PostgreSQL local (or shared dev) instance, dedicated `WellnessBuddyDev` database

### When AI providers activate (Sprint 5)

- Add `httpx.AsyncClient` per provider (don't share — each manages its own timeouts/retries)
- Add `tenacity` for retry logic on Ollama/OpenAI/Anthropic calls
- Add `tiktoken` if implementing OpenAI token counting for budget guards
- Frontend: `react-use-websocket` `^4.x` if AI chat moves to streaming over WebSocket; otherwise SSE via native `EventSource`

---

## Version Compatibility Matrix

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| React 19.2 | TypeScript 5.6+ | Required for new types (`use`, server actions, ref-as-prop) |
| React 19.2 | TanStack Query v5 | Full support; v5.50+ optimizes for React 19 transitions |
| React 19.2 | motion ^12 | Confirmed support; framer-motion legacy package also works |
| React 19.2 | react-hook-form ^7.53 | Confirmed |
| Tailwind v4 | shadcn/ui (latest CLI) | Native v4 support since shadcn rewrite; old v3 components must be re-added via CLI |
| Tailwind v4 | Vite 7 | First-class via `@tailwindcss/vite` plugin |
| Vite 7 | vite-plugin-pwa ^0.21 | Works |
| Dexie 4.4 | TanStack Query v5 | Use community `@tanstack-dexie-db-collection` OR roll your own with `useLiveQuery` + `queryClient.invalidate()` |
| FastAPI 0.136 | Pydantic v2.7+ | Required (Pydantic v1 dropped) |
| FastAPI 0.136 | SQLAlchemy 2 async | Standard pairing |
| FastAPI 0.136 | Python 3.10+ | 3.12 recommended |
| WeasyPrint 62 | Windows Server 2019 | Requires GTK3 Runtime (one-time MSI install) |
| Uvicorn 0.30 | Python 3.12 | Use `uvicorn[standard]` for `httptools` + `uvloop` (note: uvloop NOT available on Windows — falls back to asyncio, still fine for 100 users) |

---

## Key Add-On Prescriptions for the Win Requisite

For the project to feel "elite elegant + playful", these specific additions beyond the contract pin are non-negotiable:

1. **Geist font family** (npm `geist`) — installed via Next-style font loader pattern adapted for Vite. Replace any default Inter/system-ui choice.
2. **Motion** for every state transition — page transitions, meal-card variant switch, weight chart point appearance, checkbox toggles. Spring physics, not linear easing.
3. **Lottie** for at least 5 moments: app first-launch hero, empty `/today` (no plan uploaded), shopping list cleared (celebration), workout streak milestone, weight goal reached. Use minimal stroke style packs only.
4. **Custom illustration kit** sourced from Storyset (consistent style) — colorize per design tokens. One vibrant accent + warm neutrals.
5. **shadcn/ui Form + Card + Tabs + Calendar** as base components, customized aggressively (not used vanilla).
6. **Sonner toasts** with custom styling matching the warm palette — use them for every async outcome (saved, synced, exported).
7. **Tailwind v4 `@theme` design tokens** — define `--color-warm-coral`, `--color-leaf-green`, `--font-display`, `--radius-card`, and force EVERY component to consume tokens (no hardcoded hex). This is what separates "elegant" from "competent".
8. **Mascot character** introduced Sprint 3 — single character, three expressions, used at empty states and milestones. Avocado/measuring-tape ribbon are common nutrition tropes; consider a more original choice (e.g., a "wellness buddy" friendly anthropomorphic water-droplet or scale spirit).

---

## Sources

### Verified (HIGH confidence)
- [React Versions — react.dev](https://react.dev/versions) — React 19.2.5 latest as of April 2026
- [Vite 7.0 announcement — vite.dev](https://vite.dev/blog/announcing-vite7) — Stable June 2025
- [Vite 8.0 announcement — vite.dev](https://vite.dev/blog/announcing-vite8) — Stable March 2026 (we hold at v7)
- [Tailwind CSS v4 vs v3 (2026) — Frontend Hero](https://frontend-hero.com/tailwind-v4-vs-v3) — v4 is greenfield default
- [Tailwind CSS Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide) — Official migration path
- [shadcn/ui — ui.shadcn.com](https://ui.shadcn.com/) — Default 2026 component approach
- [Motion docs — motion.dev](https://motion.dev/) — Renamed from framer-motion mid-2025
- [Dexie.js — dexie.org](https://dexie.org/) — v4.4.2 latest, liveQuery primary API
- [TanStack Query v5 docs](https://tanstack.com/query/v5/docs/framework/react) — Server-state separation
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/) — 0.136.1 (April 2026)
- [Geist Font — vercel.com/font](https://vercel.com/font) — Free, npm-installable
- [Lucide vs Phosphor 2026 — wmtips.com](https://www.wmtips.com/technologies/compare/lucide-vs-phosphor-icons/) — Lucide 16x dominant
- [Recharts vs Tremor vs Nivo 2026 — PkgPulse](https://www.pkgpulse.com/guides/recharts-v3-vs-tremor-vs-nivo-react-charting-2026)
- [Sonner vs react-hot-toast — PkgPulse](https://www.pkgpulse.com/compare/react-hot-toast-vs-sonner) — Sonner 9.7x lead
- [date-fns v4 vs Temporal vs Day.js — PkgPulse](https://www.pkgpulse.com/guides/date-fns-v4-vs-temporal-api-vs-dayjs-date-handling-2026)
- [vite-plugin-pwa — vite-pwa-org.netlify.app](https://vite-pwa-org.netlify.app/) — Workbox 7 integration
- [Top 10 Python PDF generators 2026 — Nutrient](https://www.nutrient.io/blog/top-10-ways-to-generate-pdfs-in-python/)
- [Lottie vs Rive 2026 — Callstack](https://www.callstack.com/blog/lottie-vs-rive-optimizing-mobile-app-animation)
- [FastAPI Deployment Windows IIS — hoop.dev](https://hoop.dev/blog/the-simplest-way-to-make-fastapi-iis-work-like-it-should/)
- [React Hook Form + Zod 2026 — DEV Community](https://dev.to/marufrahmanlive/react-hook-form-with-zod-complete-guide-for-2026-1em1)

### MEDIUM confidence (single-source or community wisdom)
- Storyset / Open Doodles illustration sourcing — design industry common knowledge
- WeasyPrint Windows GTK3 runtime requirement — verified via WeasyPrint docs but production reliability needs Sprint 1 spike confirmation
- Custom mascot recommendation — design-craft opinion, not a measurable fact

---

*Stack research for: Wellness Buddy — self-hosted nutrition tracking PWA*
*Researched: 2026-05-01*
*Verified against: React 19.2.5, Vite 7/8, Tailwind 4.0, FastAPI 0.136.1, Dexie 4.4.2, Motion v12, Recharts v3*
