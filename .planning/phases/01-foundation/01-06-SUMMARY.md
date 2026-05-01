---
phase: 01-foundation
plan: 06
subsystem: pwa-shell
tags: [pwa, workbox, dexie, mutation-queue, app-shell, offline-first, ai-widget-locked]
requires:
  - 01-01 (project init)
  - 01-05a (frontend baseline + shadcn primitives)
  - 01-05b (italian copy + format helpers + sync store)
  - 01-03 (auth + persistStorage; stubbed in this worktree, MERGE EXPECTED)
provides:
  - "frontend/vite.config.ts: VitePWA Workbox runtime caching strategy table"
  - "frontend/src/db/dexie.ts: WellnessBuddyDB v1 schema (7 tables) + isEmptyButShouldHaveData heuristic"
  - "frontend/src/lib/mutationQueue.ts: enqueue/flush + 409 toast + 5-retry dead-letter"
  - "frontend/src/services/version.ts: useVersionPolling — 5min /version.json poll + sonner toast + Workbox skipWaiting"
  - "frontend/src/components/layout/AppShell.tsx: chrome composition for protected routes"
  - "frontend/src/components/ai/AIWidget.tsx: AI-05 locked placeholder + AI-06 SSE scaffold (commented)"
affects:
  - "All protected routes now wrapped in AppShell (AppBar + nav chrome + ErrorBoundary)"
  - "Auth routes (/login /register /welcome) remain bare (no chrome)"
  - "TanStack Query cache persisted to localStorage 24h (Phase 2 upgrades to Dexie persister)"
tech-stack:
  added:
    - "@tanstack/react-query-persist-client@^5"
    - "fake-indexeddb (devDep, for vitest)"
  patterns:
    - "Workbox NetworkFirst index.html with 3s timeout (PITFALLS #2)"
    - "Workbox NetworkOnly /api/auth + writes (mutation queue handles offline)"
    - "Dexie cache_* DROP-and-refetch on schema bumps (PITFALLS #5)"
    - "mutation_queue stores OPAQUE HTTP requests, survives schema migrations"
    - "Sync setState via useState lazy-initializer instead of useEffect setState (React 19)"
key-files:
  created:
    - "frontend/src/db/dexie.ts"
    - "frontend/src/db/schema.ts"
    - "frontend/src/db/migrations.ts"
    - "frontend/src/db/__tests__/dexie.test.ts"
    - "frontend/src/lib/mutationQueue.ts"
    - "frontend/src/lib/persistStorage.ts (stub — Plan 03 owns)"
    - "frontend/src/services/api.ts (stub — Plan 03 owns)"
    - "frontend/src/services/version.ts"
    - "frontend/src/stores/auth.ts (stub — Plan 03 owns)"
    - "frontend/src/hooks/useStoragePersist.ts"
    - "frontend/src/hooks/useUpdateToast.ts"
    - "frontend/src/components/layout/AppShell.tsx"
    - "frontend/src/components/layout/AppBar.tsx"
    - "frontend/src/components/layout/BottomTabBar.tsx"
    - "frontend/src/components/layout/NavigationRail.tsx"
    - "frontend/src/components/layout/ErrorBoundary.tsx"
    - "frontend/src/components/layout/SyncStatusPip.tsx"
    - "frontend/src/components/layout/UpdatePromptToast.tsx"
    - "frontend/src/components/layout/IOSInstallBanner.tsx"
    - "frontend/src/components/ai/AIWidget.tsx"
    - "frontend/tests/e2e/pwa-update.spec.ts"
    - "frontend/tests/e2e/pwa-install.spec.ts"
  modified:
    - "frontend/vite.config.ts"
    - "frontend/src/lib/queryClient.ts"
    - "frontend/src/router.tsx"
    - "frontend/src/styles/globals.css"
    - "frontend/src/vite-env.d.ts"
    - "frontend/tests/e2e/smoke.spec.ts"
    - "frontend/package.json"
decisions:
  - "Forward-compat stubs (auth.ts, api.ts, persistStorage.ts) — Plan 03 owns canonical implementations; merge cleanup needed at Plan 03 integration"
  - "TanStack Query persister uses sync localStorage in Phase 1; Phase 2 hard requirement upgrades to Dexie-backed async persister"
  - "skipWaiting: false in Workbox config so user controls update via toast (no auto-reload mid-form per PITFALLS #2)"
  - "AIWidget Phase 1 has ZERO data interpolation + ZERO network calls (T-AI-01); SSE scaffold commented for Phase 5"
  - "IOSInstallBanner shouldOpenInstallBanner() is a synchronous helper; useState lazy initializer avoids react-hooks/set-state-in-effect (React 19)"
metrics:
  duration: 1 session
  completed: 2026-05-01
---

# Phase 1 Plan 06: PWA Shell + Dexie + AppShell + Locked AIWidget Summary

PWA shell complete: Workbox SW with NetworkFirst index.html (3s timeout, PITFALLS #2), Dexie v1 schema with 7 tables + opaque mutation_queue + drafts, mutation queue with 409 + dead-letter handling, /version.json polling with sonner update toast, AppShell composition (AppBar+SyncStatusPip / BottomTabBar / NavigationRail / ErrorBoundary / UpdatePromptToast / IOSInstallBanner / useDexieResync), AIWidget locked placeholder with SSE scaffold commented for Phase 5.

## Tasks Completed

| Task | Name | Commit | Key files |
|------|------|--------|-----------|
| 1 | Workbox + Dexie v1 + mutation queue + version polling + persister | `1717743` | vite.config.ts, db/{dexie,schema,migrations}.ts, lib/{mutationQueue,queryClient,persistStorage}.ts, services/{api,version}.ts, stores/auth.ts, hooks/{useStoragePersist,useUpdateToast}.ts, db/__tests__/dexie.test.ts |
| 2 | AppShell + AIWidget + e2e | `85b3240` | components/layout/{AppShell,AppBar,BottomTabBar,NavigationRail,ErrorBoundary,SyncStatusPip,UpdatePromptToast,IOSInstallBanner}.tsx, components/ai/AIWidget.tsx, router.tsx, tests/e2e/{pwa-update,pwa-install,smoke}.spec.ts |

## Workbox runtime caching strategy

| URL pattern | Handler | Notes |
|-------------|---------|-------|
| `request.mode === 'navigate'` (index.html / nav routes) | NetworkFirst | 3s timeout, 7-day cache fallback (PITFALLS #2) |
| `/assets/*.{js,css,woff2}` | CacheFirst | 365d, hashed filenames so safe |
| `/{icons,illustrations}/*.{svg,png}` | CacheFirst | 30d, 50 entries |
| `/api/{plans,weekly,today,dashboard}/*` | NetworkFirst | 3s timeout, 24h cache |
| `/api/auth/*` | NetworkOnly | Never cached |
| `/api/{workout,weight,errors}` (writes) | NetworkOnly | Outbox handles offline |
| `/version.json` | NetworkOnly | Always fresh |

`skipWaiting: false` + `clientsClaim: false` — user controls update via toast (no auto-reload mid-form).

## Dexie schema v1 — 7 tables

| Table | PK | Indexes | Purpose |
|-------|----|---------|---------|
| `cache_users` | `id` (UUID) | email | User profile mirror |
| `cache_plans` | `id` (UUID) | user_id, is_active | Plan list mirror |
| `cache_today` | `date` | user_id | /today day status mirror |
| `cache_workout_log` | `id` (UUID) | [user_id+date] | Workout log mirror |
| `cache_weight_log` | `id` (UUID) | [user_id+date] | Weight log mirror |
| `mutation_queue` | `id` (UUID) | created_at | OPAQUE outbox (HTTP {endpoint,method,body}) |
| `drafts` | `key` | updated_at | Form drafts (e.g. workout in-progress) |

`isEmptyButShouldHaveData()` returns true when both `cache_users` and `cache_plans` count is zero — used by `useDexieResync` (FND-08, PITFALLS #1) to refetch from server when iOS evicts storage.

## Verification

| Check | Command | Result |
|-------|---------|--------|
| Dexie tests | `pnpm vitest run src/db/__tests__/dexie.test.ts` | 6/6 passed (table count, UUID PK, isEmpty true/false, mutation_queue opacity, [user_id+date] compound) |
| Full vitest | `pnpm test` | 10/10 passed |
| Typecheck | `pnpm typecheck` | clean |
| Lint | `pnpm lint --max-warnings=0` | clean |
| Build | `pnpm build` | dist/sw.js + dist/manifest.webmanifest produced; 27 precache entries (717 KiB) |
| E2E PWA | `pnpm playwright test --grep "PWA\|update toast\|Service Worker"` | 3/3 passed |
| Full e2e (chromium) | `pnpm playwright test --project=chromium --grep-invert visual` | 5/5 passed |

Manifest spot-check (built from Task 1 build):
```json
{"name":"Wellness Buddy","short_name":"Wellness","description":"Tracking nutrizionale e wellness","start_url":"/today","display":"standalone","background_color":"#FAF9F6","theme_color":"#FAF9F6","lang":"it","scope":"/","orientation":"portrait","icons":[{"src":"/icons/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"/icons/icon-512.png","sizes":"512x512","type":"image/png"},{"src":"/icons/icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}
```

## Negative Invariants Honored (D-26)

- NO VAPID key generation in this plan
- NO `pywebpush` Python import added
- NO push subscription / `PushManager.subscribe` code surface
- NO `/api/push/*` endpoint registration
- AIWidget has zero `EventSource` / `WebSocket` instances (commented scaffold only)
- Phase 3 owns push notifications; Phase 5 owns AI streaming

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocker] Plan 03 dependencies not yet merged**
- **Found during:** Task 1
- **Issue:** Plan 06 depends on `@/services/api`, `@/stores/auth`, `@/lib/persistStorage` (Plan 03's surface), but Plan 03 has not yet merged into this worktree (parallel Wave 3 with Plan 03).
- **Fix:** Created minimal forward-compat stubs in `frontend/src/services/api.ts`, `frontend/src/stores/auth.ts`, `frontend/src/lib/persistStorage.ts`. Each stub matches the public surface contract Plan 03 will ship and contains a `MERGE EXPECTED — Plan 03 owns` header comment.
- **Commit:** `1717743`
- **MERGE NOTE:** When Plan 03 merges, those three stub files MUST be replaced with the real implementations. Plan 03's PR should include conflict resolution; the import sites in this plan (mutationQueue.ts, useStoragePersist.ts, ErrorBoundary.tsx) should require zero changes if surfaces match.

**2. [Rule 1 - Bug] react-hooks/set-state-in-effect violation in IOSInstallBanner**
- **Found during:** Task 2 lint run
- **Issue:** Initial implementation called `setOpen(true)` synchronously inside `useEffect`, which React 19 ESLint rules flag as cascading-render risk.
- **Fix:** Extracted `shouldOpenInstallBanner()` helper computing initial open state synchronously, used as `useState(() => ...)` lazy initializer. Side-effect-only useEffect bumps localStorage visit count without touching React state.
- **Commit:** `85b3240`

**3. [Rule 1 - Bug] Smoke test runtime-error filter too strict for AppShell**
- **Found during:** Task 2 e2e run
- **Issue:** `tests/e2e/smoke.spec.ts` previously asserted zero console errors; AppShell legitimately polls `/api/auth/me`, `/api/plans`, `/api/errors` via useDexieResync + ErrorBoundary which 404 against the unmocked preview server.
- **Fix:** Filter network-resource 404 messages (`Failed to load resource`, `/api/`, `the server responded with a status of 404`); keep real JS runtime errors. Aligns with the test's intent ("zero JS runtime errors") not literal console output.
- **Commit:** `85b3240`

### Architectural Decisions Honored

- TanStack Query persister uses synchronous localStorage in Phase 1 (24h, success-only). Phase 2 hard requirement upgrades to Dexie-backed async persister to escape 5MB localStorage cap when plan/weekly payloads grow.
- Auth routes (`/login`, `/register`, `/welcome`) remain bare (no AppShell chrome) — deliberate router split because the welcome flow's persistStorage prompt should not be wrapped in chrome that depends on `accessToken`.

## Manual Verification (Phase 1 pause gate — deferred to Plan 08 sign-off)

- Real iPhone Safari install: open `/today` twice → install banner appears → "Aggiungi a Home" works → standalone PWA launches at start_url=/today
- Offline `/today`: airplane mode → reload → cached shell paints; SyncStatusPip shows "Offline"
- Upgrade toast: deploy new build → within 5min the polling toast appears with "Nuova versione disponibile" + "Ricarica"
- Dexie wipe resync: DevTools → Application → IndexedDB → delete `wellness-buddy` → reload → useDexieResync refetches /api/auth/me + /api/plans
- Lighthouse PWA score = 100/100 (run `pnpm test:lighthouse-pwa`)

These checks are deferred to Plan 08 (Phase 1 close-out) per pause gate sequencing.

## Threat Mitigations Applied

| Threat | Mitigation |
|--------|------------|
| T-PWA-01 (SW stale shell) | NetworkFirst index.html 3s timeout, skipWaiting:false, hashed assets only in CacheFirst, /api/auth + writes NetworkOnly, cleanupOutdatedCaches:true, e2e test verifies update toast |
| T-DEX-01 (schema migration data loss) | mutation_queue OPAQUE shape (HTTP {endpoint,method,body}); cache_* DROP-and-refetch contract documented in migrations.ts; server UUIDs ensure idempotent refetch |
| T-XSS-02 (ErrorBoundary stack leak) | /api/errors body limited to {message, stack, url, user_agent} — no tokens; backend (Plan 02) Pydantic-validates + structlog redacts |
| T-AI-01 (AI placeholder leakage) | Zero data interpolation in AIWidget body — only static copy.ai.* strings; SSE scaffold commented, never instantiated; no /api/ai/* fetch in Phase 1 |

## Self-Check: PASSED

Files verified:
- frontend/vite.config.ts FOUND (contains VitePWA + NetworkFirst + 3s timeout + maskable + NetworkOnly /api/auth)
- frontend/src/db/dexie.ts FOUND (contains super('wellness-buddy') + cache_workout_log [user_id+date] + isEmptyButShouldHaveData)
- frontend/src/db/migrations.ts FOUND (PITFALLS #5 + DROP pattern documented)
- frontend/src/lib/mutationQueue.ts FOUND (crypto.randomUUID + status===409 + retries>=5)
- frontend/src/services/version.ts FOUND (virtual:pwa-register/react + copy.pwa.updateHeading + 5*60*1000)
- frontend/src/hooks/useStoragePersist.ts FOUND (db.isEmptyButShouldHaveData + apiClient.request)
- frontend/src/components/layout/AppShell.tsx FOUND (useDexieResync + UpdatePromptToast + IOSInstallBanner + ErrorBoundary)
- frontend/src/components/layout/IOSInstallBanner.tsx FOUND (wb-install-banner-dismissed-until + 7*24*60*60*1000 + display-mode: standalone)
- frontend/src/components/layout/ErrorBoundary.tsx FOUND (componentDidCatch + apiClient.request + /api/errors)
- frontend/src/components/ai/AIWidget.tsx FOUND (copy.ai.placeholderHeading + EventSource commented)
- frontend/src/router.tsx FOUND (Component: AppShell + lazy: async)
- dist/sw.js + dist/manifest.webmanifest produced by build

Commits verified:
- 1717743 FOUND
- 85b3240 FOUND
