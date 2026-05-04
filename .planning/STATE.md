---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: in_progress
last_updated: "2026-05-04T11:35:30Z"
progress:
  total_phases: 5
  completed_phases: 0
  total_plans: 18
  completed_plans: 15
  percent: 83
---

# State: Wellness Buddy

**Last updated:** 2026-05-04 (Phase 2 in progress — Plans 02-01..02-05 complete; 02-06 PDF is next)

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

- **Phase:** 2 — Differentiators
- **Plan:** 02-05 complete (shopping list aggregation + 5-category mapper + APScheduler weekly reset cron + /spesa route + BroadcastChannel multi-tab sync shipped). Plans 02-01..02-05 complete; 02-06 (PDF) next in queue.
- **Status:** **Phase 1 COMPLETE code-side; Phase 2 in progress.** Plans 02-01 (GTK3 spike + PdfExporter ABC), 02-02 (/settimana + variant selector), 02-03 (production deploy), 02-04 (grid parser + per-day variants), 02-05 (shopping list end-to-end) merged. Real Stefano + Marta plans now parse end-to-end and the /spesa endpoint returns 43 categorized items from Stefano's plan in 5 fixed buckets. Plans 02-06 (PDF), 02-07 (family sync), 02-08 (closure) ready to execute.
- **Progress:** Phase 1/5 done code-side · Phase 2: Plans 5/8 complete · 3 plans remaining (02-06..08)
- **Phase progress bar:**

  ```text
  [##########] 100% — Phase 1: Foundation (10/10 plans, code-side closure)
  [######....]  63% — Phase 2: Differentiators (5/8 plans complete)
  ```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Phases complete | 0 / 5 |
| Plans complete | 10 / 10 (Phase 1) |
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
| 01-04 md-parser  | ~50 min  | 3/3   | 22 created +  4 modified | 5       |
| 01-07 today      | ~75 min  | 3/3   | 20 created + 10 modified | 4       |
| 01-08 mockups+dep| ~50 min  | 2/2   | 15 created (T3 deferred) | 4       |
| 01-09 lifesum-px | ~28 min  | 3/3   | 4 created + 22 modified  | 3       |
| 02-04 grid-parser| ~25 min  | 3/3   | 7 created + 10 modified  | 3       |
| 02-05 shopping   | ~32 min  | 3/3   | 24 created + 9 modified  | 5       |

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
- (Plan 07) Greeting period buckets server-computed in user IANA tz: morning 5-12, afternoon 12-18, evening 18-23, night 23-5 — UI-SPEC §7.2 honest greeting at 23:00 across DST flips
- (Plan 07) Cross-user reads on shareable resources return 404 (not 403) — V13 information-disclosure mitigation; matches Plan 04 plan_service. /api/weight + /api/workout PATCH/DELETE never reveal existence of another user's row.
- (Plan 07) Weight upsert uses manual IntegrityError race retry instead of pg-native ON CONFLICT — keeps service vendor-portable for Phase 4 RLS / SQLite test alternative
- (Plan 07) WeightChart asserts CSS variables at the source level (read .tsx + grep) instead of jsdom SVG inspection — Recharts ResponsiveContainer collapses to 0×0 in headless DOM. Source-level check is the tighter PITFALLS#8 contract.
- (Plan 07) ResizeObserver polyfill in `frontend/src/test/setup.ts` (Rule 3 — Radix primitives reference it via @radix-ui/react-use-size; jsdom doesn't ship it; without polyfill any test mounting Switch/Checkbox/Tabs throws ReferenceError)
- (Plan 07) `--text-display-serif` Instrument Serif token usage verified by grep: theme.css (definition) + pages/Today.tsx (single consumer) — UI-SPEC §3.2 escape hatch honored
- (Plan 02-04) Dual-mode parser pattern: try grid format `| Giorno | Opzione A | Opzione B |` first, fall back to `### Opzione X` subheading on empty result. Reusable for any future MD section format the project encounters.
- (Plan 02-04) `lunches` and `dinners` parsed_json shape is `dict[str, list[MealOption]]` keyed by Italian day_slug (`lun`..`dom`) for grid format, `default` for subheading format. Backward compat preserved.
- (Plan 02-04) WeeklyPlanVariant composite UNIQUE constraint `(user_id, week_start, day_of_week, meal_type)` replaces week-level uniqueness; alembic 8137b2e24001.
- (Plan 02-04) today_service threads `variant_by_meal: dict[str, WeeklyPlanVariant]` into `_meals_from_parsed` so user's stored selection overrides first-option default — recipe title shown matches chosen variant.
- (Plan 02-04) /api/weekly response includes `options: list[MealOptionPayload]` per (day, slot) so frontend variant selector can map UI A/B/special to actual backend grid keys (`opzione_a`/`opzione_b`/`piatto`/...).
- (Plan 02-04) Italian-keyed `dayLabels` (`lun`..`dom`) added to `copy.it.ts` alongside legacy `mon`..`sun` aliases — both work; canonical is Italian short form matching grid parser.
- (Plan 02-05) Pure-aggregation core pattern — `_aggregate_ingredients(meals: list[dict])` is DB-free and unit-tested; `aggregate_for_week` orchestrates plan + variant fetches and delegates.
- (Plan 02-05) Shopping aggregation key is `(canonical_name, unit)` tuple — same-name-different-unit splits into separate rows; q.b. (unit='qb') collapses count=1 regardless of recipe count (Pitfall #14).
- (Plan 02-05) Meal-level `**Categoria:**` annotation wins over keyword lookup ONLY when it matches one of the 5 locked categories (Frigo & Freschi / Frutta & Verdura / Dispensa / Condimenti / Integratori); else falls back to Dispensa (T-02-05-01 STRIDE).
- (Plan 02-05) APScheduler 3.11.2 has a documented spring-forward edge case where `day_of_week='mon', hour=0` skips one week when seeded BEFORE DST Sunday; fall-back works correctly. Documented in scheduler.py header. Real-world impact: ~once per 5 years, user can manually POST /reset.
- (Plan 02-05) `PYTEST_CURRENT_TEST` lifespan guard — long-lived background services (scheduler) opt out during pytest so test_engine fixtures can recreate the DB without ObjectInUseError on `DROP DATABASE`.
- (Plan 02-05) BroadcastChannel + window.focus listener fallback for iOS Safari Private mode multi-tab sync (D-25, Pitfall #15) — 3 unit tests cover delivery, unsubscribe, and fallback paths.
- (Plan 02-05) Native `<details><summary>` for ShoppingCategorySection collapsible — zero JS state, full keyboard a11y inherited.
- (Plan 02-05) BowlSteam icon used for Condimenti instead of Wine (kitchen-objects WIN REQUISITE) — better semantic match for sauces/oils/condiments.

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

**`/gsd:execute-phase 02-differentiators`** — Phase 2 in progress. Plans 02-01..02-05 complete (shopping list end-to-end shipped). Wave 6 = 02-06 (shopping PDF — wires WeasyPrint exporter from Plan 02-01 + `build_pdf_payload` from 02-05) ready to execute next.

### Phase 2 Plan Index

| Plan | Title | Wave | Status |
|------|-------|------|--------|
| 02-01 | WeasyPrint GTK3 spike + PdfExporter ABC | 1 | done |
| 02-02 | /settimana + variant selector + LWW 409 | 2 | done |
| 02-03 | Production deploy CHECKPOINT | 3 | done |
| 02-04 | Gap-closure: weekly grid parser + per-day variants | 4 | done (commits 745fd96, b97cbc1, c6f1241) |
| 02-05 | Shopping list | 5 | done (commits 52e0753, 8f8748d, 8810764, 50270db, 55f94f7) |
| 02-06 | Shopping PDF | 6 | ready |
| 02-07 | Family sync | 7 | not started |
| 02-08 | Phase 2 closure CHECKPOINT | 8 | not started |

---
*State initialized: 2026-05-01 — Phase 1 (Foundation) is the current focus.*
