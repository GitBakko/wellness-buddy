<!-- GSD:project-start source:PROJECT.md -->
## Project

**Wellness Buddy** — Progressive Web App (PWA) self-hosted per tracking nutrizionale e wellness, multi-user con family meal sync. React 19 + FastAPI + PostgreSQL su Windows Server 2019. Caso d'uso: Stefano + Marta Brunelli con piani nutrizionali distinti e cene/pranzi condivisi. Max 100 utenti.

**Core Value:** L'utente segue il piano nutrizionale in modo aderente e visibile — ogni pasto chiaro, spesa generata, peso e allenamento tracciati senza attrito. Se tutto il resto fallisce: "vedo cosa devo mangiare oggi e segno il peso".

**WIN REQUISITE (non-negotiable):** UI/UX a metà tra eleganza/minimal e giocoso/friendly, ELITE quality. Senza questo il progetto è fallito. Usare attivamente skill `impeccable:*` (frontend-design, polish, delight, colorize, animate, harden, adapt, critique).

Vedi `.planning/PROJECT.md` per requirements, constraints e key decisions.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

**Frontend:** React 19.2 · Vite 7 · **TailwindCSS 4** (`@theme` tokens) · TypeScript 5.6 · Zustand 5 · TanStack Query v5 · Dexie.js 4.4 · react-router 7 · vite-plugin-pwa 0.21 · Workbox

**UI/UX:** shadcn/ui + Radix · Motion v12 · Lottie + Rive (Sprint 3) · lucide-react · Geist Sans/Mono · sonner · cva + tailwind-merge · Storyset/Open Doodles illustrations · Recharts 3 · react-hook-form + zod · date-fns v4

**Backend:** Python 3.12 · FastAPI 0.136 · SQLAlchemy 2 async + asyncpg · Pydantic v2 · Alembic · Uvicorn (1 worker via NSSM) · python-jose + passlib[bcrypt] · **WeasyPrint** (primary) + ReportLab (fallback) · python-markdown · pywebpush · APScheduler

**Dev tooling:** Vitest · Playwright + axe-core · ESLint 9 flat · Prettier · ruff · mypy · pnpm workspaces

**Deployment:** Windows Server 2019 · IIS reverse proxy · win-acme SSL · PostgreSQL (existing)

**AI providers (Sprint 5):** Ollama (GX10 ARM64, gemma3:27b) · OpenAI · Anthropic — tutti dietro `AIProvider` ABC

Vedi `.planning/research/STACK.md` per versioni puntuali e rationale.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

**Code:**
1. Mobile-first 390px → tablet → desktop con container queries
2. Italian-only Sprint 1 — tutti label/messaggi in `frontend/src/i18n/copy.it.ts`
3. JWT access 15 min in memory (Zustand) · refresh 7 giorni HttpOnly cookie + rotation
4. API errors sempre JSON `{detail: string, code: string}`
5. AI layer SEMPRE astratto via `AIProvider` ABC — nessuna chiamata diretta Ollama/OpenAI/Anthropic in business logic
6. Solo Alembic per migrazioni DB — mai modificare schema direttamente
7. Server è canonical truth, Dexie è cache + outbox queue (mai source of truth)
8. UUIDs server-generated, mai auto-int PKs in Dexie
9. TIMESTAMPTZ + UTC storage + IANA timezone su User (default `Europe/Rome`)
10. `group_id` MAI in JWT — sempre re-look-up da DB per multi-user authz
11. Cross-user reads via `get_user_with_group_access(target_user_id)` dependency, mai riusare `get_current_user` per shared paths
12. MD parser tollerante in `parsers/`, validation strict via Pydantic in `schemas/plan_parsed.py`
13. Conflict resolution: last-write-wins + version int + 409 → toast UX
14. Visibility enum su shareable resources: `private` | `group_shared` (cene+pranzi default shared, weight+workout always private)

**UI/UX (WIN REQUISITE — every PR):**
1. Tutti colori/font/radius/motion via Tailwind 4 `@theme` tokens — **mai hardcoded hex**
2. Motion budget: ≤250ms micro-transitions, ≤800ms celebrations, ≤2 simultaneous moving elements, `ease-out-soft`
3. `prefers-reduced-motion: reduce` honored via `--motion-scale: 0`
4. Touch microinteractions: tap scale 0.97 con 80ms ease
5. Dark mode first-class: palette OKLCH/HSL con dark variants da day one, Recharts via CSS vars, screenshot tests CI
6. axe-core CI ≥4.5:1 body / ≥3:1 large icons · Lighthouse a11y ≥95
7. Illustrations: decorative `aria-hidden`, meaningful `<title>` + `aria-labelledby` italiani
8. Form errors: italian copy + icon + `role="alert"` + color (mai color alone)
9. iOS keyboard: `visualViewport` API + scroll input into view
10. Tone: NO `!` in error messages · NO infantile mascots · empty states minimalist italiani
11. `Intl.NumberFormat('it-IT')` · 24h time · NFC normalize · `Intl.Collator('it')` sorting
12. Emoji ≤1-2 per screen in copy only, mai chrome
13. ≤1 celebration per session, mai blocca user input
14. Mascot Sprint 3: original (water-droplet/scale-spirit), **NON** trope avocado

**Git:**
- Solo Alembic per migrations
- Pause gates a fine ogni fase (Phase 1: real iPhone install + axe-core green + Lighthouse PWA 100/100)

Vedi `.planning/REQUIREMENTS.md` per checklist UI-01 → UI-20.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

**3-tier offline-first:**

```
[React 19 PWA on iPhone/Android]
  ├─ Zustand (auth-in-mem + UI state + theme)
  ├─ TanStack Query (server resources, mirrored to Dexie via persistQueryClient)
  ├─ Dexie.js (cache_* tables + mutation_queue + drafts)
  └─ Workbox SW (NetworkFirst index.html, CacheFirst hashed assets)
        ↕ HTTPS via IIS reverse proxy + Let's Encrypt
[FastAPI 0.136 on Windows Server 2019]
  ├─ Uvicorn 1 worker via NSSM
  ├─ AIProvider ABC (Depends → app.state singleton, factory at lifespan startup)
  ├─ Tolerant MD Parser → strict Pydantic v2 schemas
  ├─ Auth: access in-memory + refresh HttpOnly cookie + rotation + family-revocation + 10s grace
  └─ APScheduler (Mon 07:00 push reminders DST-aware)
        ↕ asyncpg pool 15/10
[PostgreSQL — canonical truth]
  ├─ TIMESTAMPTZ everywhere
  ├─ Group + visibility enum for multi-user sync
  └─ Row-Level Security (Sprint 4 defense-in-depth)
```

**State split:**
- Zustand: auth/UI/theme
- TanStack Query → Dexie (server resources)
- Dexie alone: drafts + mutation queue
- CacheStorage (Workbox): HTTP responses + assets

**Build order locks:**
- Models (Phase 1) before any feature
- Auth (Phase 1) before user-scoped endpoints
- MD Parser (Phase 1) before /today
- AI ABC (Phase 1) before any AI endpoint
- Group entity (Phase 1 schema) before family sync (Phase 2)
- VAPID keys (Phase 3) before push reminders
- TIMESTAMPTZ + IANA tz (Phase 1) before notifications (Phase 3)

Vedi `.planning/research/ARCHITECTURE.md` per pattern dettagliati e DI sketches.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.

**Recommended skills to invoke during UI sprints (already installed in Claude Code, not project-local):**
- `impeccable:frontend-design` — costruisce UI distintive
- `impeccable:polish` — alignment/spacing/dettagli pre-ship
- `impeccable:delight` — momenti di gioia
- `impeccable:colorize` — palette strategica
- `impeccable:animate` — micro-interazioni e motion
- `impeccable:harden` — error handling, i18n, edge cases
- `impeccable:adapt` — responsive cross-device
- `impeccable:critique` — UX evaluation
<!-- GSD:skills-end -->

<!-- GSD:session-continuity-start source:GSD defaults -->
## Session Continuity

If `.planning/HANDOFF.json` exists at the start of a session, a previous session was interrupted (for example by `/compact` or `/gsd:pause-work`) and its state is captured there.

Run `/gsd:resume-work` immediately — before anything else, without waiting for user input. The resume skill will restore context, show project status, and clean up the handoff file.

This instruction is a backup path. When the SessionStart hook fires it emits the same directive via systemMessage; either trigger is sufficient.
<!-- GSD:session-continuity-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` — do not edit manually.
<!-- GSD:profile-end -->
