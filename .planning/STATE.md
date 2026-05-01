# State: Wellness Buddy

**Last updated:** 2026-05-01 (Plan 01-03 auth complete — Wave 3 parallel landing alongside 01-06)

## Project Reference

- **Project:** Wellness Buddy
- **What:** Self-hosted PWA per nutrition + wellness tracking, multi-user famiglia, AI pluggabile
- **Core value:** L'utente segue il piano nutrizionale in modo aderente e visibile — ogni pasto chiaro, spesa generata, peso e allenamento tracciati senza attrito. Minimo: "vedo cosa devo mangiare oggi e segno il peso".
- **WIN REQUISITE:** UI/UX a metà tra eleganza/minimal e giocoso/friendly — non-negotiable
- **Source of truth:** `.planning/PROJECT.md`
- **Requirements:** `.planning/REQUIREMENTS.md` (~145 v1, 100% mapped to phases)
- **Roadmap:** `.planning/ROADMAP.md` (5 phases)
- **Research:** `.planning/research/SUMMARY.md` (HIGH confidence)

## Current Position

- **Phase:** 1 — Foundation
- **Plan:** 01-03 complete (Wave 3 parallel branch alongside 01-06); auth fully wired both backend + frontend
- **Status:** Wave 3 complete — both Plans 03 (auth) and 06 (PWA shell) shipped; ready for Wave 4 (Plans 04, 07, 08)
- **Progress:** Phase 0/5 phases complete · Plans 4/10
- **Phase progress bar:**
  ```
  [####      ] 40% — Phase 1: Foundation (4/10 plans)
  ```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Phases complete | 0 / 5 |
| Plans complete | 4 / 10 (Phase 1) |
| v1 requirements mapped | 145 / 145 (100%) |
| Orphan requirements | 0 |
| Pause gates passed | 0 / 5 |

### Plan execution metrics

| Phase-Plan       | Duration | Tasks | Files                    | Commits |
|------------------|----------|-------|--------------------------|---------|
| 01-01 monorepo   | ~10 min  | 3/3   | 30 created + 1 modified  | 3       |
| 01-05b fe-behave | ~25 min  | 2/2   | 20 created + 3 modified  | 2       |
| 01-06 pwa-shell  | 1 sess   | 2/2   | 22 created + 7 modified  | 2       |
| 01-03 auth       | ~20 min  | 2/2   | 10 created + 11 modified | 4       |

## Accumulated Context

### Key Decisions Carried Forward

(From PROJECT.md — verbatim, do not repeat unless changed)
- TailwindCSS 4 (override of contract v3) for WIN REQUISITE UI/UX foundation
- WeasyPrint primary + ReportLab fallback for shopping list PDF (Sprint 2 GTK3 spike validates)
- Vite 7 (hold for Sprint 1 stability, re-evaluate Sprint 4)
- pnpm workspaces only (no Turborepo Sprint 1)
- Auth: access in memory + refresh HttpOnly cookie + rotation + 10s grace window
- Server canonical truth, Dexie cache + outbox queue
- Group entity in schema Sprint 1 (avoid late FK migration)
- TIMESTAMPTZ + IANA tz on User from Sprint 1 (DST correctness)
- Italian-only Sprint 1 via constants file (refactor to react-i18next only if non-Italian users emerge)
- AI provider DI via `Depends(get_ai_provider)` from Sprint 1, NullProvider default
- Last-write-wins conflict resolution + 409 toast UX
- (Plan 05b) Italian copy lives in `frontend/src/i18n/copy.it.ts` as single source of truth (114 strings, 13 namespaces, FND-09)
- (Plan 05b) `useSyncExternalStore` adopted for `useMediaQuery` to satisfy `react-hooks/set-state-in-effect`
- (Plan 05b) Visual diff via Playwright `toHaveScreenshot()` (no Percy); `maxDiffPixelRatio=0.02` per spec
- (Plan 05b) Test infra runs against `pnpm preview` built bundle (Pitfall #12) — never `pnpm dev`
- (Plan 06) Workbox NetworkFirst index.html with 3s timeout (PITFALLS #2 mitigation), skipWaiting:false (no auto-reload mid-form)
- (Plan 06) Dexie v1 schema with 7 tables; mutation_queue stores OPAQUE HTTP requests (PITFALLS #5 — survives schema bumps); cache_* DROP-and-refetch contract
- (Plan 06) TanStack Query persister uses sync localStorage Phase 1; Phase 2 hard requirement upgrades to Dexie-backed async persister
- (Plan 06) Forward-compat stubs for auth/api/persistStorage shipped — Plan 03 owns canonical impls (MERGE EXPECTED at 03 integration)
- (Plan 06) AIWidget Phase 1 ships locked placeholder with SSE/WebSocket scaffold COMMENTED — zero data interpolation, zero network calls (T-AI-01); D-26 negative invariant honored (no VAPID, no pywebpush, no push API surface)
- (Plan 03) Refresh-rotation 10s grace lives in `auth_service.rotate_refresh` (cached_access/cached_refresh on the row) — middleware passthrough; backend coverage 96% on auth surface (≥80% gate)
- (Plan 03) Frontend singleton refresh promise in `lib/refreshTokenAtomic.ts` — 5 concurrent 401s coalesce to 1 fetch (Vitest verified); resets via `setTimeout(0)` so subsequent batches refetch
- (Plan 03) `bcrypt<4.1` pinned because passlib 1.7.4 reads `bcrypt.__about__.__version__` removed in 4.1
- (Plan 03) Test DB on port 5434 via `docker-compose.override.yml` (5432 occupied by another project's container on dev box) — production wiring unaffected
- (Plan 03) Test fixture isolation via `TRUNCATE ... RESTART IDENTITY CASCADE` BEFORE each `db_session` yield (committed rows otherwise persisted between tests)
- (Plan 03) Coverage of SQLAlchemy async paths needs `concurrency = ["thread", "greenlet"]` — without it auth_service.py reported 51% instead of 93%
- (Plan 03) Test emails use `*.example.com` because email-validator rejects `.local` as a special-use TLD

### Open Questions to Resolve in Plans

1. Shared meal default opt-in/opt-out (recommendation: cene+pranzi `group_shared`, breakfast/snacks `private`) — confirm with Marta during Phase 2 planning
2. Push permission UX (settings only, never auto-prompt) — confirm Phase 3
3. Bundle size budget — lazy-load `/progress` and `/admin` from day one (lock Phase 1)
4. PostgreSQL backup strategy — confirm with Stefano (existing NXTLink tooling)
5. Real-time strategy for `condiviso` badge — start polling 30s, WS only if complaints (decide Phase 2)
6. Mascot character concept (water-droplet vs scale-spirit, NOT avocado) — decide Phase 3 mockup review
7. Tone ratio elegant/playful (scene-by-scene, not pixel-by-pixel) — lock via Phase 1 mockup review with Stefano+Marta
8. WeasyPrint Windows GTK3 production stability — Phase 2 spike validates before locking
9. Vite 7 vs 8 upgrade — hold v7 for Phase 1, re-evaluate Phase 4
10. AI streaming protocol — SSE for Phase 5

### Blockers

(none — ready to plan Phase 1)

### TODO Backlog (cross-phase)

- Locate Stefano + Marta MD plans, copy into `/plans/` repo path before Phase 1 `/today` testing
- Confirm domain `wellness-buddy.epartner.it` DNS pointing to Windows Server 2019 before win-acme cert request
- Verify GTK3 Runtime MSI download URL still valid before Phase 2 spike

## Session Continuity

### Files of record
- `.planning/PROJECT.md` — vision, constraints, key decisions
- `.planning/REQUIREMENTS.md` — ~145 v1 reqs, traceability table locked
- `.planning/ROADMAP.md` — 5 phases, success criteria, pause gates
- `.planning/research/SUMMARY.md` — research synthesis (HIGH confidence)
- `.planning/research/STACK.md` / `FEATURES.md` / `ARCHITECTURE.md` / `PITFALLS.md` — depth references
- `.planning/config.json` — granularity standard, mode yolo, parallelization on

### Hard dependency locks (must respect during planning)
- Group entity in schema Sprint 1 (Phase 1) even though family sync arrives Sprint 2 (Phase 2)
- AI ABC + NullProvider Sprint 1 (Phase 1) before any AI endpoint
- MD parser Sprint 1 (Phase 1) before /today
- Auth Sprint 1 (Phase 1) before anything user-scoped
- Variants API (Phase 2) before Shopping List (Phase 2)
- VAPID keys (Phase 3) before push reminders (Phase 3)
- TIMESTAMPTZ + IANA tz (Phase 1) before notifications (Phase 3)
- WIN REQUISITE foundations (tokens, axe-core CI, dark-mode CI screenshots, tone mockups) Phase 1 — every later phase inherits, never retrofits

### Pause gates roadmap
- **Phase 1 gate:** Real iPhone install + offline /today + upgrade path + Dexie wipe resync + axe-core green + Lighthouse PWA 100/100 + tone calibration locked
- **Phase 2 gate:** Family-sync authz matrix verde + PDF Italian accents on iPhone Safari/Mail + condiviso badge convergence ≤5s + GTK3 stability decision
- **Phase 3 gate:** DST notification test verde + VoiceOver pass + dark mode contrast green + tone review Stefano+Marta
- **Phase 4 gate:** RLS tests verde + k6 ramp test verde p95 <500ms + admin a11y pass + Vite upgrade decision
- **Phase 5 gate:** Prompt-injection adversarial corpus verde + cost-cap simulation verde + family isolation verde + kill-switch tested

### Next Action

Wave 4 — execute Plans 01-04 (MD parser pipeline) and 01-07 (/today landing) in parallel. Plan 01-08 (tone calibration mockups + DEPLOY.md) follows.

---
*State initialized: 2026-05-01 — Phase 1 (Foundation) is the current focus.*
