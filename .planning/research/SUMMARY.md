# Project Research Summary — Wellness Buddy

**Project:** Wellness Buddy — self-hosted nutrition tracking PWA (multi-user, offline-first, AI-pluggable)
**Domain:** Plan-driven nutrition/wellness tracking, family-oriented, Italian-first
**Researched:** 2026-05-01
**Overall confidence:** HIGH

---

## Executive Summary

Wellness Buddy sits in the **plan-driven** half of the 2026 nutrition app market (Eat This Much, Plan to Eat, Prospre) — **not** the food-database half (MyFitnessPal, Cronometer). Its differentiation is the unique combination of (1) Markdown plan as source of truth, (2) multi-user family meal sync with shared cene/pranzi, (3) self-hosted privacy, and (4) elite-quality elegant+playful UI/UX. No competitor combines those four. The contract-pinned stack (React 19, Vite 7, Zustand, TanStack Query v5, Dexie 4, FastAPI, SQLAlchemy 2 async, PostgreSQL) is the canonical 2026 default and validates cleanly — with two pin overrides recommended (Tailwind v4 over v3, WeasyPrint over a contested PDF choice).

The recommended approach is a **3-tier offline-first architecture**: React 19 PWA on the device with Dexie+TanStack Query as offline cache and durable mutation queue, FastAPI single-process backend on Windows Server 2019 behind IIS reverse proxy, PostgreSQL as canonical truth. Authentication uses **JWT access in memory + refresh in HttpOnly cookie with rotation**. AI is wired Sprint 1 as an `AIProvider` ABC with `NullProvider` so endpoints function before real providers land in Sprint 5. Multi-user sync uses a `Group` entity with a `visibility` flag on shareable resources — last-write-wins with 409 conflicts surfaced to UX. The MD parser is **tolerant** with strict Pydantic v2 validation downstream.

The dominant risks are **iOS-specific** (storage eviction silently wipes IndexedDB, stale `index.html` traps users on old SW versions, push works only on installed PWAs since 16.4), **multi-user authorization** (group leakage, JWT staleness, race conditions on shared meals), and **WIN REQUISITE drift** (animations failing `prefers-reduced-motion`, dark mode bolted on late, contrast failing WCAG AA on the warm palette, tone slipping toward infantile). Each is mitigated with concrete patterns landed in Sprint 1 architecture and verified at every UI sprint via axe-core CI gates and real-device QA.

---

## Key Findings

### Cross-Cutting Themes (across all 4 dimensions)

1. **Server is canonical truth, every client cache is disposable.** Dexie is a fast mirror + outbox queue, never the source. This single rule resolves storage-eviction, schema-migration, and conflict headaches.
2. **The contract pins are right except in two places** — Tailwind v3 should be v4 (materially advances UI/UX win); PDF library is contested between STACK and ARCHITECTURE (resolved below toward WeasyPrint with ReportLab fallback).
3. **Sprint 1 must over-invest in foundations that are expensive to retrofit.** Auth refresh-rotation, Group entity (even unused), TIMESTAMPTZ everywhere, AI provider DI, tolerant MD parser, network-first SW for `index.html`, persistent storage request, axe-core CI gate — all land Sprint 1 even if their consumers come later.
4. **Plan-driven discipline is non-negotiable.** Anti-feature drift toward food databases / barcode scanners / wearable sync would destroy the Core Value.
5. **WIN REQUISITE UI/UX is a cross-cutting concern**, not a phase. Every sprint needs design tokens, motion budget, dark-mode parity, accessibility gate, and tone calibration.

### Recommended Stack (final picks)

**Frontend core:** React 19.2 · Vite 7 · **TailwindCSS 4** (override of contract v3) · TypeScript 5.6 · Zustand 5 · TanStack Query v5 · Dexie.js 4.4 · react-router 7 · vite-plugin-pwa 0.21 · workbox-window 7

**UI/UX layer (the WIN REQUISITE stack):** shadcn/ui + Radix · cva + tailwind-merge + clsx · **Motion** (framer-motion successor) v12 · Lottie now + Rive in Sprint 3 · **lucide-react** icons · **Geist Sans + Geist Mono** typography · Storyset/Open Doodles illustrations · sonner toasts · tailwindcss-animate

**Charts/forms/dates:** Recharts 3 · react-hook-form 7 + zod 3 + @hookform/resolvers · date-fns v4 · react-day-picker 9 · react-markdown + remark-gfm

**Backend core:** Python 3.12 · FastAPI 0.136 · SQLAlchemy 2 async + asyncpg · Pydantic v2.7 · Alembic · Uvicorn (1 worker, NSSM Windows service) · python-jose + passlib[bcrypt] · python-multipart

**Backend supporting:** **WeasyPrint** primary + ReportLab fallback · python-markdown · pywebpush · httpx · APScheduler

**Dev tooling:** Vitest · Playwright · ESLint 9 flat · Prettier + prettier-plugin-tailwindcss · ruff · mypy · pnpm workspaces (no Turborepo Sprint 1)

### Feature Strategy

**Table stakes (Sprint 1 must-have):** /today landing · meal completion · weight log+chart · workout log · MD plan upload+parser · JWT auth · mobile-first 390px · PWA installable · offline /today + /shopping · light/dark · edit/delete · macro display.

**Differentiators (Sprint 2-3):** MD-as-source-of-truth · multi-user family meal sync with `condiviso` badge · variant selector A/B/Pasta · auto-shopping list · weight projection band ±0.5 kg/sett · plan diff · lunedì pesata ritual · single elegant streak counter + adherence ring · Italian-first UX · AI provider abstraction.

**Anti-features (active scope discipline):** food database · barcode scanner · recipe library+photos · calorie burn auto-calc · wearable sync · public registration · social/feed · badges/XP/levels/leaderboards · daily nag notifications · AI photo recognition · in-app purchases · public meal sharing · automatic workout detection · micronutrient tracking · meal photo journal.

### Architecture Pillars (top 7)

1. **3-tier offline-first** with server-canonical truth: React PWA (Dexie cache + mutation queue) ↔ FastAPI ↔ PostgreSQL. No CRDT.
2. **State-split rule:** auth/UI/theme → Zustand · server resources → TanStack Query (mirrored to Dexie via `persistQueryClient`) · drafts + mutation queue → Dexie · HTTP+assets → CacheStorage. Never duplicate.
3. **AI provider DI** (`Depends(get_ai_provider)`), built once at app startup via factory + `app.state` singleton. `NullProvider` Sprint 1; concrete providers Sprint 5.
4. **Tolerant MD parser → strict Pydantic schema.** API never sees raw dicts. `parse_and_validate(md) -> (PlanParsedSchema, ParseReport)`.
5. **Multi-user sync via `Group` + `visibility` enum**, not direct user-to-user FKs. Cene + pranzi default `group_shared`; weight + workout always private. Group exists Sprint 1 schema.
6. **Auth: access token in memory + refresh in HttpOnly+Secure+SameSite=Lax cookie with rotation + family-revocation + 10s grace window** to avoid mobile-resume race-condition logout storms. Singleton refresh promise client-side.
7. **Service Worker strategy by resource:** `index.html` and shell **NetworkFirst** (never precache navigation HTML); hashed `/assets/*` CacheFirst; `/api/plans|weekly` NetworkFirst with 3s timeout; `/api/auth` and writes NetworkOnly. Mutation queue in Dexie, replayed on `online` event.

### Critical Pitfalls (top 5 to prevent in Sprint 1)

1. **iOS PWA storage eviction wipes IndexedDB silently.** Mitigation: `navigator.storage.persist()` after first login; on app boot if Dexie empty but JWT valid, full-resync from server before showing UI; "Last synced X min ago" UI.
2. **Service Worker caches `index.html` aggressively → users stuck on old version.** Mitigation: NetworkFirst for shell, cache-bust on every deploy, explicit update toast with `skipWaiting` + postMessage, `/version.json` polling. Test upgrade path on real iPhone.
3. **JWT refresh race on iPhone resume → logout storm.** Mitigation: singleton refresh promise client-side + 10s server-side idempotent grace window + preemptive refresh when access expires <60s + refresh in HttpOnly cookie.
4. **MD parser brittle on real-world content** (BOM/CRLF/NBSP/smart quotes/decomposed Unicode). Mitigation: normalization pipeline (`utf-8-sig` → `\r\n→\n` → NFC → NBSP→space → smart-punct→ASCII), case-insensitive heading match by stem, log+surface warnings, evil-input corpus test (Word/Notes.app/Notion/Obsidian/Notepad).
5. **WIN REQUISITE UI/UX traps** — animations, contrast, dark mode, tone drift. Mitigation: tone calibration mockups Sprint 1, motion budget honoring `prefers-reduced-motion` (`--motion-scale: 0` when reduced), dark mode first-class with CI screenshot tests, axe-core ≥95 gate, illustration `<title>` + `aria-labelledby`, copy guardrails (no infantile mascot, no exclamation in errors).

---

## Stack Decisions (final picks with conflict resolutions)

### Stack Decision 1: TailwindCSS — **v4** (deviating from contract v3)

The contract pins Tailwind v3. STACK.md recommends overriding to **v4**. We adopt v4.

**Rationale:**
- v4's **Oxide engine** delivers 2-5× faster builds.
- **Container queries** critical for responsive meal-card grid without media-query pyramids.
- **CSS-first `@theme` design tokens** are the foundation of WIN REQUISITE UI/UX.
- **shadcn/ui v4 native** support — canonical 2026 component approach.
- **Browser baseline alignment:** Tailwind v4 requires Safari 16.4+ — already required by iOS Web Push for installed PWAs. No additional browser lift.
- Single largest UI/UX win in the stack. Sticking with v3 leaves design quality on the table.

**Risk:** v4 ecosystem younger. Mitigation: shadcn, tailwindcss-animate, prettier-plugin-tailwindcss mature on v4 as of May 2026.

**Action:** Update PROJECT.md `Stack frontend` constraint and prompt contract: "TailwindCSS 4". Document deviation in CLAUDE.md.

### Stack Decision 2: PDF library — **WeasyPrint** primary, ReportLab fallback

STACK.md recommends WeasyPrint. ARCHITECTURE.md recommends ReportLab. Resolved in favor of **WeasyPrint** with explicit fallback condition.

**Rationale:**
- Shopping list is **data-driven table** — exactly the case where HTML+CSS-to-PDF beats imperative canvas drawing.
- **Reuse of Tailwind v4 `@theme` tokens via shared CSS variables** means printed Sunday-night fridge list inherits brand consistency automatically.
- **Italian text** with accents handled natively by WeasyPrint's font subsystem with proper UTF-8 + NFC normalization.
- Shopping-list PDF is a **brand touchpoint** — WeasyPrint produces "loving home brand"; ReportLab produces "office print".
- Designer iteration: CSS change vs. Python code change — orders of magnitude faster.

**Risk and mitigation — Windows GTK3:** WeasyPrint requires GTK3 Runtime on Windows Server 2019 (single MSI: `gtk3-runtime-3.24.x-msvc.exe`). One-time install, documented in DEPLOY.md.

**Fallback condition:** If GTK3 install proves unstable in production after Sprint 2 spike (PDF endpoint 5xx rate >2% over 7 days, or service-startup failures), fall back to ReportLab with Jinja-driven layout helper.

**Action:** Sprint 1 backend skeleton imports `weasyprint`. Sprint 2 ships PDF endpoint. Sprint 2 retrospective re-evaluates GTK stability before locking.

### Stack Decision 3: Vite — **v7** (hold, not v8)

Vite 8 is stable since March 2026 with Rolldown. We hold at **v7** for Sprint 1 stability; plugin ecosystem still settling. Re-evaluate at Sprint 4.

### Stack Decision 4: Monorepo tooling — **pnpm workspaces only** (no Turborepo Sprint 1)

Single frontend package today; Turborepo adds caching value only with multiple JS packages. Backend Python lives outside JS workspace.

### Stack Decision 5: Worker count — **1 Uvicorn worker** for 100 users

Async I/O handles concurrency within one event loop. Pool sizing: `pool_size=15, max_overflow=10`. Re-evaluate at Sprint 4 with real load.

### Other lock-ins (no conflict)

- **Auth:** access in memory + refresh in HttpOnly cookie + rotation + family revocation + 10s idempotent grace window
- **Conflict policy:** last-write-wins per resource + `If-Unmodified-Since` style version on PATCH + 409 → toast UX
- **MD parser:** tolerant in `parsers/`, strict in `schemas/plan_parsed.py`
- **Group entity:** ships in Sprint 1 schema even though family sync lands Sprint 2
- **TIMESTAMPTZ everywhere** + IANA timezone string on User table (default `Europe/Rome`)
- **VAPID keys:** generated once, never rotated without forced re-subscribe

---

## Roadmap Implications

### Suggested phase order (5 sprints + pause gates)

**Sprint 1 — Foundation** (must-haves expensive to retrofit)
- Monorepo + tooling (pnpm workspaces, ESLint flat, Prettier, ruff, mypy)
- Backend skeleton (FastAPI + Alembic + SQLAlchemy 2 async + asyncpg pool 15/10)
- Frontend skeleton (Vite 7 + React 19 + **Tailwind 4** + shadcn/ui CLI init)
- PostgreSQL `WellnessBuddy` DB + Alembic init
- Models including **`Group` entity** + TIMESTAMPTZ everywhere + IANA tz on User
- **Auth: JWT access (15 min, in-memory) + refresh (7 day, HttpOnly cookie) with rotation + family revocation + 10s grace window + singleton refresh promise client-side**
- Tolerant **MD parser** + strict Pydantic schemas (with evil-input corpus test)
- **PWA shell** with NetworkFirst-for-`index.html` + Workbox runtime caches + version.json polling + update toast
- **Dexie schema** with `cache_*` tables + `mutation_queue` + `drafts` (UUIDs from server, never int PKs)
- `navigator.storage.persist()` request after first login
- **AIProvider ABC + NullProvider** (wired into DI even though stub)
- Plan upload + activate + diff view (basic)
- /today landing view (single-user, no variants yet)
- Weight log + basic chart (Recharts, no projection band yet)
- Workout log toggle + duration + note
- Light/dark mode + design tokens via Tailwind 4 `@theme`
- **WIN REQUISITE foundations:** Geist Sans+Mono, lucide-react, Motion installed, sonner toasts, axe-core CI gate ≥95, dark-mode screenshot tests in CI, tone calibration mockups locked, illustration accessibility pattern documented
- Deploy to Windows Server 2019 (Uvicorn 1 worker via NSSM + IIS reverse proxy + win-acme cert)

**Sprint 1 PAUSE GATE:** real iPhone install, real offline test, real upgrade path, real resync after manual Dexie wipe, axe-core green, Lighthouse PWA 100/100.

**Sprint 2 — Differentiators**
- Weekly view + week picker + variant selector A/B/Pasta speciale
- Auto-shopping list aggregation + checkbox state in Dexie + Italian categorization
- Shopping list **PDF export via WeasyPrint** (Sprint 2 spike validates GTK3 stability)
- **Multi-user family sync** via Group + visibility, `condiviso` badge, last-write-wins with 409 toast UX, dedicated `get_user_with_group_access` dependency, comprehensive negative-authz tests in CI
- Sync queue replay refinement, conflict toast UX
- TanStack Query persistence to Dexie via `persistQueryClient`

**Sprint 2 PAUSE GATE:** family-sync authz tests pass (matrix of own/shared/private/non-family/ex-member), PDF renders Italian accents on iPhone Safari + Mail.app, `condiviso` badge converges within 5s in concurrent variant test.

**Sprint 3 — Engagement & polish**
- Weight projection band ±0.5 kg/sett (Recharts ReferenceArea)
- KPI dashboard cards + streak counter + adherence ring
- Lunedì check-in special copy + UI state
- VAPID keys + Push API subscription + APScheduler weekly Mon 07:00 reminder in user's IANA timezone (DST test)
- Plan diff view polish (semantic diff)
- **Rive in `/progress` hero**
- Custom mascot character (3 expressions, water-droplet or scale-spirit)
- Lottie celebrations: first weight log, 7-day streak, weight goal hit (≤1 per session, ≤800ms)

**Sprint 3 PAUSE GATE:** DST notification test green, mobile-VoiceOver pass on every screen, contrast audit green in dark mode, tone review with Stefano+Marta confirms balance.

**Sprint 4 — Admin & hardening**
- Admin panel: user management, invite tokens (24h expiry, single-use, revocable), plan assignment, audit log
- Plan archive + history
- PostgreSQL Row-Level Security as defense-in-depth
- Connection pool + load test (k6 simulating morning resume storm)
- Re-evaluate Vite 7→8 upgrade decision

**Sprint 4 PAUSE GATE:** RLS tests pass, k6 ramp test green, admin panel a11y pass.

**Sprint 5 — AI activation**
- Ollama provider (GX10 ARM64, gemma3:27b, 60s first-request timeout)
- OpenAI + Anthropic providers with rate limit + max_tokens=500 hard cap + per-user daily quota + kill-switch `AI_PROVIDER=null` env
- AI capabilities endpoint + frontend feature detection
- AI features: meal suggestion, week analysis, shopping tips
- AI chat widget unlocked: streaming via SSE, `<user_note>...</user_note>` delimited prompts, output validation, family isolation

**Sprint 5 PAUSE GATE:** prompt-injection adversarial corpus tests green, cost-cap simulation cleanly rate-limited.

### Hard dependency locks

| Must precede | Reason |
|--------------|--------|
| Models (Sprint 1) before any feature | Schema must exist; Group entity Sprint 1 even unused |
| Auth (Sprint 1) before anything user-scoped | Every protected endpoint needs `Depends(get_current_user)` |
| MD Parser (Sprint 1) before /today | Everything visual flows from parsed plan |
| AI ABC (Sprint 1) before any AI endpoint | Even stubs need the type |
| Variants API (Sprint 2) before Shopping List | List aggregates from selected variants |
| Group entity (Sprint 1 schema) before family sync (Sprint 2) | Avoid late FK migration churn |
| VAPID keys (Sprint 3) before push reminders | Server can't sign push without keys |
| TIMESTAMPTZ + IANA tz (Sprint 1) before notifications (Sprint 3) | DST correctness depends on schema discipline |

### Sprint 1 must-haves (non-negotiable)

- Group entity in schema (even unused until Sprint 2)
- TIMESTAMPTZ + IANA tz on User
- AI provider ABC + NullProvider
- Refresh token rotation + family revocation + 10s grace window
- NetworkFirst for `index.html`
- `navigator.storage.persist()` request flow
- UUIDs from server, never auto-int PKs in Dexie
- Tolerant MD parser → strict Pydantic split
- Tailwind 4 `@theme` design tokens
- axe-core CI gate ≥95 + dark-mode screenshot CI tests + `prefers-reduced-motion` honored
- Tone calibration mockups locked + reviewed by Stefano+Marta

---

## WIN REQUISITE UI/UX Strategy (dedicated section — non-negotiable)

The brief: *"eleganza minimal + tocco giocoso/friendly, ELITE quality"*. Without this the project is failed. This section is the operating manual.

### Philosophy

**Elegant baseline + playful surface accents.** Defaults are calm, restrained, typographically refined. Playfulness shows up in *moments* — celebratory micro-animations, custom illustrations at empty states, lunedì ritual UI variant, mascot expressions at milestones — never in chrome of routine flows. The 50/50 ratio is **scene-by-scene**, not pixel-by-pixel: daily meal log scene tilts 70% elegant; streak-milestone scene tilts 70% playful. Validated via Sprint 1 tone calibration mockups (3 sliders 25/50/75) reviewed by Stefano+Marta.

### Design tokens (Tailwind 4 `@theme`)

Every component consumes these — **never** hardcoded hex.

- **Colors (OKLCH or HSL with explicit dark variants):** `--color-warm-coral`, `--color-leaf-green`, neutrals (50→950 with light + dark axis), semantic (success/warning/error WCAG AA-verified)
- **Typography:** `--font-sans` = Geist Sans · `--font-mono` = Geist Mono (KPI/weight values, tabular nums) · `--font-display` = Instrument Serif (optional, max one heading per page)
- **Radius:** `--radius-card`, `--radius-button`, `--radius-pill`
- **Motion:** `--motion-scale` (1 normally, 0 when `prefers-reduced-motion: reduce`) · `--ease-out-soft` · `--duration-fast` (150ms) · `--duration-base` (250ms) · `--duration-celebration` (≤800ms)

### Library stack (layered)

```
LAYER 4 — Delight:    Lottie (Sprint 1+) + Rive (Sprint 3 progress hero)
LAYER 3 — Motion:     Motion v12 — every state transition
LAYER 2 — Components: shadcn/ui + Radix UI primitives (WAI-ARIA out of the box)
LAYER 1 — Primitives: Tailwind v4 + @theme tokens
```

**Other key picks:** lucide-react icons · cva + tailwind-merge + clsx for variants · sonner toasts · Storyset/Open Doodles illustrations (NOT unDraw monochrome blue) · Lottie for ≤5 specific moments · custom mascot Sprint 3 (water-droplet or scale-spirit, **not** trope avocado).

### Motion budget (enforced every sprint)

- **Max 250ms** per micro-transition
- **≤800ms** for celebration moments
- **≤2 simultaneous moving elements** per screen
- **`ease-out-soft`** spring physics, never linear
- **`prefers-reduced-motion: reduce` honored** by `--motion-scale: 0`
- **≤1 celebration per session**, never blocks input
- **Touch microinteractions:** every tap scales 0.97 with 80ms ease

### Accessibility gates (CI-enforced from Sprint 1 PR #1)

- **axe-core in Playwright** on every PR — fail at <4.5:1 body, <3:1 large/icons
- **Lighthouse a11y ≥95** on every UI route
- **Dark mode screenshot tests** for every page
- **VoiceOver smoke test** every sprint on real iOS device
- **Illustrations:** decorative SVG `aria-hidden="true"` · meaningful SVG `<title>` + `aria-labelledby` Italian copy
- **Form errors:** Italian copy + icon + `role="alert"` + color
- **iOS keyboard:** `visualViewport` API + scroll input into view

### Dark mode is first-class (not bolted on)

- Palette in OKLCH/HSL with explicit dark variants from day one
- Recharts: `stroke` and `fill` from CSS variables, never hardcoded
- Theme color in PWA manifest with `media` queries for dark/light
- Every screen tested in dark mode via CI screenshot tests

### Tone guardrails (the "infantile mascot" trap)

- **No exclamation marks in error messages.** "Sessione scaduta dopo 7 giorni di inattività. Accedi di nuovo." not "Ops! Devi rifare il login!"
- **Empty states:** illustration + minimalist Italian copy ("Nessun pasto registrato"), never "Ops! Sembra che non hai ancora mangiato 🍔!"
- **No infantile mascots.** Sprint 3 mascot is single character with 3 expressions used **only at milestones + empty states**.
- **Reserve playfulness for celebratory moments:** routine data display stays elegant.
- **Italian formatting:** `Intl.NumberFormat('it-IT')` everywhere · 24h time · NFC normalize · `Intl.Collator('it')` for sorting
- **Emoji budget:** ≤1-2 per screen in COPY ONLY, never in UI chrome.
- **Tone-of-voice in Italian:** warm, slightly playful but never silly.

### Cross-phase discipline (UI/UX lens applied every sprint)

- **Sprint 1:** tone calibration mockups locked → Stefano+Marta review → ratio decided. Design tokens defined. Dark mode + a11y CI gates land.
- **Sprint 2:** every new component inherits tokens. PDF inherits brand via shared CSS variables.
- **Sprint 3:** mascot introduced. Lottie + Rive celebrations land with constraints enforced. Lunedì ritual UI variant.
- **Sprint 4:** admin panel respects same tokens (no "office app" drift).
- **Sprint 5:** AI chat widget streaming UX with skeleton placeholders + "Sto pensando..." dots.

### `impeccable:*` skills to invoke

Per PROJECT.md WIN REQUISITE: actively use `impeccable:frontend-design`, `impeccable:polish`, `impeccable:delight`, `impeccable:colorize`, `impeccable:animate`, `impeccable:harden`, `impeccable:adapt`, `impeccable:critique` across UI sprints. Run `impeccable:critique` and `impeccable:harden` after each sprint close.

---

## Open Questions (consolidated, deduplicated)

1. **Shared meal opt-in vs opt-out per family?** Recommendation: cene+pranzi `group_shared` default, breakfast/snacks `private`, UI toggle. Confirm with Marta during Sprint 2 planning.
2. **Push permission UX:** Recommendation: settings only — never auto-prompt. Confirm Sprint 3.
3. **Bundle size budget:** lazy-load `/progress` (Recharts) and `/admin` from day one via `React.lazy`. Lock Sprint 1.
4. **Backup strategy for PostgreSQL:** confirm with Stefano (existing NXTLink backup tooling).
5. **Real-time strategy for `condiviso` badge:** start with polling (TanStack Query refetch on focus + 30s `staleTime`), add WS only if complaints. Decide Sprint 2 research.
6. **Mascot character concept:** original (water-droplet or scale-spirit), not trope avocado. Decide Sprint 3 mockup review.
7. **Tone ratio (elegant/playful):** scene-by-scene (routine = 70/30 elegant; celebrations = 30/70 playful). Lock via Sprint 1 mockup review.
8. **WeasyPrint Windows GTK3 production stability:** Sprint 2 spike validates. Fallback to ReportLab if blocking.
9. **Vite 7 vs 8 upgrade:** hold v7 for Sprint 1 stability; re-evaluate Sprint 4.
10. **Italian-only or i18n architecture:** Italian-only with constant file Sprint 1; refactor to i18n only if non-Italian user emerges.
11. **AI streaming protocol:** SSE Sprint 5 (simpler, sufficient for chat).

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | **HIGH** | All key picks verified against 2026 official docs; conflicts explicitly resolved with rationale and fallback. |
| **Features** | **HIGH** | Multiple 2026 competitive sources cross-referenced; explicit anchoring to PROJECT.md + PROMPT_CONTRACT. |
| **Architecture** | **HIGH** | Patterns verified from official sources. MEDIUM only on conflict-resolution policy and worker count under burst. |
| **Pitfalls** | **HIGH** | Cross-verified with WebKit blog, Workbox tracker, OWASP, PostgreSQL official, Auth0. |

**Overall confidence: HIGH.**

### Gaps to address during planning/execution

- WeasyPrint Windows GTK3 production stability — Sprint 2 spike before locking; ReportLab fallback documented.
- WIN REQUISITE tone ratio — Sprint 1 mockup review with Stefano+Marta locks 25/50/75 slider per scene type.
- Conflict resolution UX for shared meals — Sprint 2 research-phase decides poll vs WS vs SSE.
- Real-iPhone QA cadence — every sprint, not just Sprint 1.
- Pool sizing under real load — Sprint 4 k6 ramp test confirms or adjusts.
- AI cost caps + prompt injection corpus — Sprint 5 first PR.

---
*Research synthesis completed: 2026-05-01*
*Ready for roadmap: yes*
