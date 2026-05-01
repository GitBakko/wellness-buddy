---
phase: 01-foundation
plan: 05b
subsystem: frontend-behavior
tags: [i18n, italian, format-helpers, hooks, zustand, testing, vitest, playwright, axe-core, lighthouse, visual-diff, accessibility, motion-budget]
dependency-graph:
  requires:
    - "01-01 (frontend manifest + ESLint base)"
  provides:
    - "frontend/src/i18n/copy.it.ts (FND-09 single source of truth for Italian UI strings)"
    - "frontend/src/lib/format.ts (UI-18 Italian Intl helpers)"
    - "frontend/src/hooks/* (useReducedMotion, useOnline, useMediaQuery, useTheme, useToast, useDebounce)"
    - "frontend/src/stores/* (theme persisted, ui, sync)"
    - "frontend/vitest.config.ts + src/test/setup.ts (jsdom unit test runtime)"
    - "frontend/playwright.config.ts (axe + visual-light + visual-dark + iphone-13 + chromium projects)"
    - "frontend/lighthouserc.json (a11y >= 0.95 + PWA = 1.0 thresholds)"
    - "tests/e2e/{smoke,a11y}.spec.ts + tests/visual/{light,dark}.spec.ts + src/styles/__tests__/motion.test.ts"
  affects:
    - "Plans 03/04/06/07 (consume copy.it.ts + format.ts + hooks + stores)"
    - "Plan 05a (parallel — provides theme.css, main.tsx, router, build pipeline this plan's tests run against)"
    - "Phase 1 CI workflows (Plan 01) — these tests gate every PR"
tech-stack:
  added:
    - "vitest@4.1.5"
    - "@testing-library/react@16.3.2"
    - "@testing-library/jest-dom@6.9.1"
    - "@testing-library/user-event@14.6.1"
    - "jsdom@29.1.1"
    - "@playwright/test@1.59.1"
    - "@axe-core/playwright"
    - "@lhci/cli"
    - "react@19.2"
    - "zustand@5"
    - "sonner@2.0.7"
    - "typescript@5.9.3"
    - "eslint@9 + typescript-eslint + eslint-plugin-react + eslint-plugin-react-hooks"
  patterns:
    - "Italian copy as single source of truth (FND-09): copy.it.ts exported `as const`, type-safe via `Copy = typeof copy`"
    - "Intl helpers built once at module load (NUMBER_FMT, DATE_FMT_*, COLLATOR), exported as thin functions — never `toLocaleString()` ad-hoc (RESEARCH 'Don't Hand-Roll')"
    - "useSyncExternalStore for matchMedia subscriptions (React 19 idiomatic, no setState-in-effect cascade)"
    - "Zustand persist middleware on theme store ('wb-theme' localStorage key) + onRehydrateStorage hook to sync DOM on boot"
    - "Playwright projects split by concern (axe, visual-light, visual-dark, iphone-13, chromium) all running against `pnpm preview --port 4173` (Pitfall #12 — built dist not dev)"
    - "Visual diff using Playwright's built-in toHaveScreenshot, no Percy dependency"
    - "Lighthouse CI thresholds enforce a11y ≥ 0.95 + PWA = 1.0 as hard errors; performance + best-practices as warnings"
    - "Test setup injects motion budget tokens via inline <style> so getComputedStyle reads work in jsdom"
key-files:
  created:
    - "frontend/src/i18n/copy.it.ts (114 strings, 13 namespaces — UI-SPEC §7.2 verbatim)"
    - "frontend/src/lib/format.ts (italianNumber/Int, italianDateShort/Long, italianTime, italianCollator, parseItalianDecimal, nfc, formatWeight, formatCalories)"
    - "frontend/src/hooks/useReducedMotion.ts"
    - "frontend/src/hooks/useOnline.ts"
    - "frontend/src/hooks/useMediaQuery.ts"
    - "frontend/src/hooks/useTheme.ts"
    - "frontend/src/hooks/useToast.ts"
    - "frontend/src/hooks/useDebounce.ts"
    - "frontend/src/stores/theme.ts"
    - "frontend/src/stores/ui.ts"
    - "frontend/src/stores/sync.ts"
    - "frontend/vitest.config.ts"
    - "frontend/playwright.config.ts"
    - "frontend/lighthouserc.json"
    - "frontend/src/test/setup.ts"
    - "frontend/tests/e2e/smoke.spec.ts"
    - "frontend/tests/e2e/a11y.spec.ts"
    - "frontend/tests/visual/light.spec.ts"
    - "frontend/tests/visual/dark.spec.ts"
    - "frontend/src/styles/__tests__/motion.test.ts"
    - "frontend/tsconfig.json (minimal — Plan 05a will harden with strict + paths + project refs)"
  modified:
    - "frontend/package.json (added test + framework deps)"
    - "frontend/eslint.config.js (added *.cjs/.prettierrc.cjs/lighthouserc.json to ignores)"
    - "pnpm-lock.yaml"
decisions:
  - "Adopted `useSyncExternalStore` for useMediaQuery instead of useState+useEffect — eliminates setState-in-effect cascading renders (react-hooks/set-state-in-effect ESLint rule)."
  - "copy.it.ts exposes 114 string entries across 13 namespaces (target was ~80 in UI-SPEC §7.2; expanded to cover RESEARCH Pattern 12 keys + tone-rule descriptive comments). All strings verbatim from UI-SPEC §7.2."
  - "Visual diff uses Playwright's built-in `toHaveScreenshot()` — no Percy dependency. maxDiffPixelRatio=0.02 per spec, animations='disabled' for determinism."
  - "Lighthouse CI runs against 4 routes (/login /today /piano /impostazioni) — covers public + private + multi-step flows. PWA = 1.0 may not pass until Plan 06 ships service worker; flag noted for Plan 06 verification."
  - "Test infra deliberately runs against `pnpm preview` (built bundle), not `pnpm dev` — Pitfall #12 (dev-mode hot-reload masks production-only issues like SW registration, hashed asset paths)."
  - "tsconfig.json shipped as minimal scaffolding so `pnpm typecheck` works in this worktree; expect Plan 05a's tsconfig.json (with project refs + tsconfig.node.json) to overwrite on merge."
metrics:
  duration: "~25 min"
  completed: "2026-05-01"
  tasks: "2/2"
  files_created: 20
  files_modified: 3
  italian_strings: 114
  namespaces: 13
  hooks: 6
  stores: 3
  vitest_tests_passing: "4/4 (motion.test.ts)"
  playwright_projects: 5
  lighthouse_routes: 4
  visual_baseline_specs: "8 (4 routes × 2 schemes)"
---

# Phase 1 Plan 05b: Frontend Behavior + i18n + Test Infrastructure Summary

Italian-only copy.it.ts (114 strings, 13 namespaces — UI-SPEC §7.2 verbatim), Italian Intl helpers (number/date/time/collator/decimal-parse/NFC), 6 behavioral hooks (`useReducedMotion`/`useOnline`/`useMediaQuery`/`useTheme`/`useToast`/`useDebounce`), 3 Zustand stores (theme persisted, ui, sync), and full test infrastructure (Vitest jsdom + Playwright with axe + visual-diff + iphone-13 + chromium projects + Lighthouse CI a11y≥95 + PWA=100 thresholds + motion budget unit test).

## Objective Met

- ✅ `frontend/src/i18n/copy.it.ts` — 114 Italian strings across 13 namespaces (auth, invite, today, weight, workout, plans, settings, pwa, ai, sync, errors, appBar, appBoot), every UI-SPEC §7.2 row covered verbatim, no infantile mascots, no `!` in errors, verb-first CTAs, NFC-friendly literals.
- ✅ `frontend/src/lib/format.ts` — `Intl.NumberFormat('it-IT')` + `Intl.DateTimeFormat('it-IT')` (short + long + time-24h) + `Intl.Collator('it')` + `parseItalianDecimal` (75,3→75.3) + `nfc` + convenience `formatWeight`/`formatCalories`. Per RESEARCH "Don't Hand-Roll" — never `toLocaleString()` ad-hoc.
- ✅ Hooks: `useReducedMotion` (UI-05 prefers-reduced-motion), `useOnline` (navigator.onLine + events), `useMediaQuery` (React 19 `useSyncExternalStore`), `useTheme` (re-export), `useToast` (sonner re-export), `useDebounce`.
- ✅ Stores: `theme` (persist middleware → 'wb-theme' localStorage + `applyTheme(mode)` mutates `documentElement[data-theme]`), `ui` (currentWeekStart ISO Monday), `sync` (online + pendingMutations + lastSyncedAt — Pitfall #1 trust signal, UI-SPEC §10.5).
- ✅ Test infra: Vitest jsdom config + setup.ts (jest-dom matchers + matchMedia mock + theme tokens injected), Playwright config (5 projects, reducedMotion: 'reduce' globally, runs against `pnpm preview`), Lighthouse CI thresholds, smoke + a11y (6 routes, wcag2aa) + visual-diff (4 routes × 2 schemes) + motion budget unit test (4/4 passing).

## Files Created

20 files created, 3 modified — see frontmatter `key-files` section.

## Test Results

| Test                              | Result            |
| --------------------------------- | ----------------- |
| `pnpm typecheck`                  | ✅ pass (0 errors) |
| `pnpm lint --max-warnings=0`      | ✅ pass (0 errors) |
| `pnpm vitest run motion.test.ts`  | ✅ 4/4 passing     |
| `pnpm exec playwright install --with-deps chromium` | ✅ Playwright 1.59.1 installed |
| `pnpm build`                      | ⏸ deferred — needs Plan 05a (vite.config.ts + main.tsx + index.html) — verified at merge |
| Lighthouse PWA = 1.0              | ⏸ blocked until Plan 06 service worker ships — flag noted for Plan 06 verification |

## Initial Lighthouse / Visual Diff Baseline

- **Lighthouse runs:** 0 (deferred until Plan 05a build pipeline merges; Plan 06 SW required for PWA=100). Thresholds locked in `lighthouserc.json` (a11y ≥ 0.95 hard, PWA = 1.0 hard, performance/best-practices ≥ 0.9 warn).
- **Visual baseline screenshots:** 0 baselines captured (deferred until Plan 05a routes render real UI). Test scaffolding in place for 4 routes × 2 color schemes = **8 future baselines** (`light_login.png`, `light_today.png`, `light_piano.png`, `light_impostazioni.png` × dark equivalents).
- **Italian string count:** 114 (target ~80 from UI-SPEC §7.2; expansion driven by full coverage of nested greeting/empty-state/macro variants per RESEARCH Pattern 12).

## Decisions Made

1. **`useSyncExternalStore` for `useMediaQuery`** — Originally written with `useState`+`useEffect`, ESLint flagged `react-hooks/set-state-in-effect` (cascading renders). Rewrote using React 19's idiomatic external-store subscription pattern. Same contract, zero re-render churn, SSR-safe.
2. **Italian copy expansion** — UI-SPEC §7.2 lists ~80 surface strings; copy.it.ts ships 114 entries because greeting variants (morning/afternoon/evening/night) + nested empty-state objects (heading/body/cta) + macro chip-vs-full pairs each count as multiple keys but render single surfaces. All strings verbatim from UI-SPEC §7.2 + RESEARCH Pattern 12. No paraphrasing, no `!` in errors, no infantile copy.
3. **Visual diff with Playwright built-in** — `toHaveScreenshot()` is shipped with `@playwright/test`. No Percy / no separate visual diff service. `maxDiffPixelRatio=0.02` is the per-spec tolerance; below 1% drift passes.
4. **Test infra runs against `pnpm preview`** — Pitfall #12 enforcement. Hashed assets, real SW registration (post-Plan 06), production NODE_ENV. `pnpm dev` would mask production-only failures.
5. **`tsconfig.json` minimal scaffolding** — Plan 05a is parallel and will deliver the full tsconfig (project refs + tsconfig.node.json + vite/client types). My version unblocks `pnpm typecheck` in this worktree without conflicting with 05a's structure on merge (last-write-wins).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] tsconfig.json + minimum deps installed**

- **Found during:** Task 1 verify (`pnpm typecheck`)
- **Issue:** Plan 05a (parallel wave) owns tsconfig.json + React/Zustand/sonner deps. Without them, `pnpm typecheck` fails in this worktree.
- **Fix:** Created minimal `tsconfig.json` (strict + path alias `@/*` + types: []), installed React 19, Zustand 5, sonner, TypeScript, @types/react, ESLint 9 + plugins. All compatible with what 05a will deliver — last-write-wins on merge.
- **Files modified:** `frontend/tsconfig.json` (created), `frontend/package.json`, `pnpm-lock.yaml`
- **Commit:** `2434c6d`

**2. [Rule 1 - Bug] `useMediaQuery` setState-in-effect**

- **Found during:** Task 1 lint
- **Issue:** ESLint `react-hooks/set-state-in-effect` flagged `setMatches(mql.matches)` synchronously inside `useEffect` body — causes cascading renders.
- **Fix:** Rewrote using `useSyncExternalStore` (React 19 idiomatic). Same external contract (`(query) => boolean`), zero re-render churn, SSR-safe via `() => false` server-snapshot.
- **Files modified:** `frontend/src/hooks/useMediaQuery.ts`
- **Commit:** `2434c6d`

**3. [Rule 1 - Bug] ESLint config flagged config files**

- **Found during:** Task 1 lint
- **Issue:** `.prettierrc.cjs` (CommonJS) tripped `no-undef: module` because eslint.config.js declared `globals: { window, document, console }` only (no `module`).
- **Fix:** Added `*.cjs`, `.prettierrc.cjs`, `lighthouserc.json` to eslint.config.js `ignores` — these are config files, not source.
- **Files modified:** `frontend/eslint.config.js`
- **Commit:** `2434c6d`

### Deferred Items

**1. `pnpm build` verify (Task 2 acceptance criterion)**

- **Reason:** Plan 05a (parallel wave 2) owns `frontend/vite.config.ts`, `frontend/index.html`, `frontend/src/main.tsx`. Without those, `vite build` cannot succeed.
- **Resolution path:** Once 05a merges with this branch, run `pnpm build` to verify Task 2 build acceptance criterion. All test-infra config files are validated by `pnpm typecheck` and `pnpm vitest run`; `pnpm build` only verifies the bundle artifact, not the test infra contract.

**2. Lighthouse PWA = 1.0 (success criterion)**

- **Reason:** Plan 06 ships the service worker (vite-plugin-pwa + Workbox). PWA score = 100 requires registered SW + manifest + offline support — all Plan 06 territory.
- **Resolution path:** Plan 06 must run `pnpm test:lighthouse-pwa` and verify the PWA = 1.0 threshold passes after SW registration.

**3. Initial visual diff baselines + axe scan**

- **Reason:** Plan 05a delivers the actual page UI (routes /login /today /piano /impostazioni). Without rendered pages, baseline screenshots are blank and axe scans produce false negatives.
- **Resolution path:** After 05a merges + Plans 03/04/07 land their pages, run `pnpm test:visual --update-snapshots` to capture baselines, and `pnpm test:axe` to validate WCAG 2 AA compliance per route.

## Threat Model Coverage

| Threat ID    | Mitigation in this plan                                                                                                                |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| T-A11Y-01    | axe-core CI gate (`tests/e2e/a11y.spec.ts` covers 6 routes with `wcag2a + wcag2aa + wcag21a + wcag21aa` rulesets, expects 0 violations) |
| T-MOTION-01  | `useReducedMotion` hook (jsdom unit-tested via `motion.test.ts` — 4/4 pass), Playwright `contextOptions.reducedMotion: 'reduce'` global, motion tokens (`--motion-scale`, `--duration-*`) verified in setup.ts |

## CLAUDE.md Compliance Check

| CLAUDE.md UI rule                                                            | Compliance                                                                  |
| ---------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Italian-only Sprint 1 (rule 2 + FND-09)                                      | ✅ copy.it.ts is the single source of truth, 114 strings, no hardcoded literals introduced |
| Motion budget + prefers-reduced-motion (rules 2, 3)                          | ✅ useReducedMotion hook + motion.test.ts + Playwright reducedMotion: 'reduce' |
| `Intl.NumberFormat('it-IT')` + 24h time + NFC + `Intl.Collator('it')` (rule 11) | ✅ format.ts implements all four                                             |
| Tone: NO `!` in errors, NO infantile (rule 10)                               | ✅ copy.it.ts review — zero `!` in errors namespace, zero infantile language |
| Touch targets ≥ 44px (UI-06)                                                 | ⏳ Component-level — enforced by Plan 05a Button primitive (`min-h-11`)      |
| axe-core CI ≥ 4.5:1 / Lighthouse a11y ≥ 95 (rule 6)                          | ✅ Thresholds locked in lighthouserc.json + a11y.spec.ts; visible after pages render (Plans 03/04/07) |
| ESLint ban on hex (UI-01, FND-04)                                            | ✅ Inherited from Plan 01's eslint.config.js (`no-restricted-syntax` regex preserved) |

## Stub Tracking

None. All Task 1 + Task 2 files are functional implementations. Page placeholders for visual-diff routes are owned by Plan 05a (`pages/Login.tsx`, etc.) — out of this plan's scope.

## Self-Check: PASSED

**Files verified:**

- ✅ `frontend/src/i18n/copy.it.ts` (FOUND, 114 strings, 13 namespaces, "Buongiorno"/"Carica piano"/"Pesata di oggi"/"Nuova versione disponibile" all literal)
- ✅ `frontend/src/lib/format.ts` (FOUND, `Intl.NumberFormat('it-IT')` + `Intl.Collator('it')` + `parseItalianDecimal` + `nfc` literal)
- ✅ `frontend/src/hooks/{useReducedMotion,useOnline,useMediaQuery,useTheme,useToast,useDebounce}.ts` (all 6 FOUND)
- ✅ `frontend/src/stores/{theme,ui,sync}.ts` (all 3 FOUND, theme.ts contains `applyTheme` + `data-theme` + `persist(`, sync.ts contains `pendingMutations` + `lastSyncedAt`)
- ✅ `frontend/vitest.config.ts` + `frontend/src/test/setup.ts` (FOUND, jsdom env + matchMedia mock + --motion-scale: 1)
- ✅ `frontend/playwright.config.ts` (FOUND, all 5 projects + colorScheme + webServer + pnpm preview port 4173)
- ✅ `frontend/lighthouserc.json` (FOUND, categories:accessibility 0.95 + categories:pwa 1.0)
- ✅ `frontend/tests/e2e/{smoke,a11y}.spec.ts` (FOUND, AxeBuilder + wcag2aa)
- ✅ `frontend/tests/visual/{light,dark}.spec.ts` (FOUND, toHaveScreenshot)
- ✅ `frontend/src/styles/__tests__/motion.test.ts` (FOUND, 4/4 tests pass)

**Commits verified:**

- ✅ `2434c6d` — feat(01-05b-01): italian copy.it.ts + format.ts + hooks + zustand stores
- ✅ `92b996c` — feat(01-05b-02): test infrastructure — vitest + playwright + axe + visual diff + lighthouse + motion test
