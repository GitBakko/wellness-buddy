---
phase: 01-foundation
plan: 05b
type: execute
wave: 2
depends_on: [01]
files_modified:
  - frontend/playwright.config.ts
  - frontend/vitest.config.ts
  - frontend/lighthouserc.json
  - frontend/src/test/setup.ts
  - frontend/src/i18n/copy.it.ts
  - frontend/src/lib/format.ts
  - frontend/src/hooks/useTheme.ts
  - frontend/src/hooks/useReducedMotion.ts
  - frontend/src/hooks/useOnline.ts
  - frontend/src/hooks/useMediaQuery.ts
  - frontend/src/hooks/useToast.ts
  - frontend/src/hooks/useDebounce.ts
  - frontend/src/stores/theme.ts
  - frontend/src/stores/ui.ts
  - frontend/src/stores/sync.ts
  - frontend/tests/e2e/a11y.spec.ts
  - frontend/tests/e2e/smoke.spec.ts
  - frontend/tests/visual/light.spec.ts
  - frontend/tests/visual/dark.spec.ts
  - frontend/src/styles/__tests__/motion.test.ts
autonomous: true
requirements: [FND-09, UI-04, UI-05, UI-06, UI-10, UI-11, UI-12, UI-13, UI-14, UI-15, UI-16, UI-17, UI-18, UI-19, UI-20]
must_haves:
  truths:
    - "Italian copy.it.ts contains all UI-SPEC §7.2 strings verbatim (~80 strings)"
    - "lib/format.ts exports italianNumber, italianDateLong, italianDateShort, italianTime, italianCollator, parseItalianDecimal, nfc helpers (UI-18)"
    - "prefers-reduced-motion: reduce sets --motion-scale: 0; useReducedMotion hook returns true"
    - "Zustand stores: theme (with persist + applyTheme), ui (currentWeekStart), sync (online + pendingMutations + lastSyncedAt)"
    - "Vitest configured for jsdom unit tests with theme tokens injected via setup.ts"
    - "Playwright configured with axe + visual-light + visual-dark + iphone-13 + chromium projects"
    - "axe-core CI gate fails PR on <4.5:1 body or <3:1 large/icon contrast (UI-10)"
    - "Lighthouse PWA score = 100 + a11y >= 95 verified by lighthouserc.json"
    - "Dark-mode visual diff tests assert pixel parity per route (UI-12)"
  artifacts:
    - path: "frontend/src/i18n/copy.it.ts"
      provides: "All UI-SPEC §7.2 Italian strings"
      contains: "Buongiorno"
    - path: "frontend/src/lib/format.ts"
      provides: "Italian Intl.NumberFormat + DateTimeFormat + Collator helpers"
      contains: "Intl.NumberFormat('it-IT')"
    - path: "frontend/playwright.config.ts"
      provides: "axe + visual diff projects (UI-10, UI-12)"
      contains: "axe"
    - path: "frontend/lighthouserc.json"
      provides: "Lighthouse a11y >=95 + PWA = 100 thresholds"
      contains: "a11y"
    - path: "frontend/src/stores/theme.ts"
      provides: "useThemeStore + applyTheme function for manual data-theme override"
      contains: "applyTheme"
  key_links:
    - from: "frontend/src/components/ui/* (Plan 05a)"
      to: "frontend/src/lib/format.ts"
      via: "Components consuming italianNumber/italianDate"
      pattern: "italianNumber|italianDate"
    - from: "frontend/src/components/auth/* (Plan 03)"
      to: "frontend/src/i18n/copy.it.ts"
      via: "Italian copy strings"
      pattern: "copy\\."
---

<objective>
Land the WIN REQUISITE UI/UX foundation (split 2 of 2): Italian `copy.it.ts` (~80 strings UI-SPEC §7.2 verbatim), Italian formatting helpers (`lib/format.ts` — `Intl.NumberFormat('it-IT')`, `Intl.DateTimeFormat`, `Intl.Collator('it')`), behavioral hooks (useReducedMotion, useOnline, useMediaQuery, useTheme, useToast, useDebounce), Zustand stores (theme with persist, ui, sync), test infrastructure (Vitest jsdom config + setup.ts injecting theme tokens, Playwright with axe + visual diff + iPhone-13 + chromium projects, Lighthouse CI thresholds a11y ≥95 + PWA = 100), smoke + a11y + visual diff tests, motion budget unit test.

The build skeleton (Vite + Tailwind 4 + shadcn primitives + theme.css + main.tsx + router) is owned by Plan 05a, which lands in parallel within Wave 2.

Purpose: Plan 05a delivered the rendering substrate. This plan delivers the *behavioral* substrate — Italian copy, Italian formatting, accessibility/motion guarantees, test gates that enforce them. Per Pitfall #10: ESLint hex ban from 05a + this plan's a11y CI gate prevent token drift in every Wave 3+ feature plan.

**Co-modified files with Plan 05a:** none — 05b adds new files only (i18n, format, hooks, stores, test infra). Both plans land within Wave 2 in parallel.

Output: `pnpm test:axe` runs against built dist with 0 violations on root. `pnpm test:visual` produces baseline screenshots for light + dark per skeleton route. `pnpm test:lighthouse-pwa` returns 100/95+ thresholds.
</objective>

<execution_context>
@C:/Users/bakko/.claude/plugins/cache/gsd-plugin/gsd/2.38.8/workflows/execute-plan.md
@C:/Users/bakko/.claude/plugins/cache/gsd-plugin/gsd/2.38.8/templates/summary.md
</execution_context>

<context>
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-CONTEXT.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-RESEARCH.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-UI-SPEC.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-VALIDATION.md
@d:/Develop/AI/WellnessBuddy/.planning/REQUIREMENTS.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-05a-PLAN.md
</context>

<interfaces>
<!-- Plan 05a delivers: theme.css tokens, shadcn primitives, main.tsx + router. -->
<!-- This plan adds copy.it.ts (consumed by Plans 03/04/06/07), format.ts (consumed by Plan 07/06), -->
<!-- hooks (consumed by everywhere), Zustand stores (consumed by 03/06/07), test infra (used by everyone). -->

From `frontend/src/i18n/copy.it.ts` (this plan creates):
```ts
export const copy = {
  auth: { loginHeading, emailLabel, ..., logoutToast },
  invite: { heading, ..., tokenInvalid },
  pwa: { installHeading, updateHeading, persistDeniedHeading, ... },
  sync: { synced, pending, error, offline, ... },
  ai: { placeholderHeading, placeholderBody },
  errors: { generic500, conflict, syncFailed, boundaryHeading, ... },
  appBar: { today, history, plan, settings },
  today: { greeting, mealMarkCta, ... },
  weight: { quickLogPlaceholder, ... },
  workout: { trainedToggle, ... },
  plans: { dropzoneIdle, activateConfirm, ... },
} as const;
```

From `frontend/src/lib/format.ts`:
```ts
export const italianNumber: (n: number) => string;
export const italianNumberInt: (n: number) => string;
export const italianDateShort: (d: Date | string) => string;
export const italianDateLong: (d: Date | string) => string;
export const italianTime: (d: Date | string) => string;
export const italianCollator: Intl.Collator;
export const parseItalianDecimal: (s: string) => number;
export const nfc: (s: string) => string;
```

From `frontend/src/stores/theme.ts`:
```ts
export const useThemeStore = create<ThemeState>(...);  // persisted to localStorage 'wb-theme'
export function applyTheme(mode: 'light' | 'dark' | 'system'): void;  // mutates document.documentElement[data-theme]
```

From `frontend/src/stores/sync.ts`:
```ts
export const useSyncStore = create<{
  online: boolean;
  pendingMutations: number;
  lastSyncedAt: number | null;
  setOnline, setPending, setLastSyncedAt;
}>;
```

From hooks (each exported as named export from corresponding `frontend/src/hooks/*.ts`):
```ts
useReducedMotion(): boolean
useOnline(): boolean
useMediaQuery(query: string): boolean
useTheme(): ThemeState
useToast(): /* sonner re-export */
useDebounce<T>(value: T, ms: number): T
```
</interfaces>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Italian copy.it.ts + lib/format.ts + hooks + Zustand stores (theme/ui/sync)</name>
  <files>frontend/src/i18n/copy.it.ts, frontend/src/lib/format.ts, frontend/src/hooks/useReducedMotion.ts, frontend/src/hooks/useOnline.ts, frontend/src/hooks/useMediaQuery.ts, frontend/src/hooks/useTheme.ts, frontend/src/hooks/useToast.ts, frontend/src/hooks/useDebounce.ts, frontend/src/stores/theme.ts, frontend/src/stores/ui.ts, frontend/src/stores/sync.ts</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md (Pattern 12 copy.it.ts structure)
    - .planning/phases/01-foundation/01-UI-SPEC.md (§7.2 — every Italian string verbatim)
    - .planning/phases/01-foundation/01-CONTEXT.md (D-12 frontend test stack, italian-only Sprint 1)
  </read_first>
  <action>
    1. **`frontend/src/i18n/copy.it.ts`** — verbatim from RESEARCH Pattern 12 / UI-SPEC §7.2. Every string from UI-SPEC §7.2 table MUST be present, no abbreviation. Structure exported as `as const`. Approximately 80 keys across `auth`, `invite`, `pwa`, `sync`, `ai`, `errors`, `appBar`, `today`, `weight`, `workout`, `plans`.

       This file is the SINGLE SOURCE OF TRUTH for Italian UI strings — Plans 03/04/06/07 import from here exclusively (FND-09).

    2. **`frontend/src/lib/format.ts`** — Italian formatting helpers (UI-18):
       ```typescript
       const NUMBER_FMT = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 2 });
       const NUMBER_FMT_WHOLE = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 0 });
       const DATE_FMT_SHORT = new Intl.DateTimeFormat('it-IT', { weekday: 'short', day: 'numeric', month: 'short' });
       const DATE_FMT_LONG = new Intl.DateTimeFormat('it-IT', { weekday: 'long', day: 'numeric', month: 'long' });
       const TIME_FMT = new Intl.DateTimeFormat('it-IT', { hour: '2-digit', minute: '2-digit', hour12: false });
       const COLLATOR = new Intl.Collator('it', { sensitivity: 'base' });

       export const italianNumber = (n: number): string => NUMBER_FMT.format(n);
       export const italianNumberInt = (n: number): string => NUMBER_FMT_WHOLE.format(n);
       export const italianDateShort = (d: Date | string): string => DATE_FMT_SHORT.format(typeof d === 'string' ? new Date(d) : d);
       export const italianDateLong = (d: Date | string): string => DATE_FMT_LONG.format(typeof d === 'string' ? new Date(d) : d);
       export const italianTime = (d: Date | string): string => TIME_FMT.format(typeof d === 'string' ? new Date(d) : d);
       export const italianCollator = COLLATOR;

       /** Parse user-typed Italian decimal: "75,3" -> 75.3 */
       export const parseItalianDecimal = (s: string): number => {
         const normalized = s.replace(',', '.').trim();
         const n = Number(normalized);
         return Number.isFinite(n) ? n : NaN;
       };

       /** Italian NFC normalize for equality/sorting parity */
       export const nfc = (s: string): string => s.normalize('NFC');
       ```

    3. **Hooks** (each in its own file under `frontend/src/hooks/`):
       - **`useReducedMotion.ts`** — UI-05 (verbatim from original Plan 05 Task 2).
       - **`useOnline.ts`** — wraps `navigator.onLine` + online/offline events.
       - **`useMediaQuery.ts`** — generic media query hook with addEventListener('change').
       - **`useTheme.ts`** — re-export from `@/stores/theme` (`useTheme`, `applyTheme`, `useThemeStore`).
       - **`useToast.ts`** — re-export from `sonner` (`{ toast } from 'sonner'`):
         ```ts
         export { toast } from 'sonner';
         ```
       - **`useDebounce.ts`** — generic debounce hook:
         ```ts
         import { useEffect, useState } from 'react';

         export function useDebounce<T>(value: T, ms: number): T {
           const [debounced, setDebounced] = useState(value);
           useEffect(() => {
             const t = setTimeout(() => setDebounced(value), ms);
             return () => clearTimeout(t);
           }, [value, ms]);
           return debounced;
         }
         ```

    4. **Zustand stores** under `frontend/src/stores/`:
       - **`theme.ts`** (UI-07 + manual data-theme + persist middleware) — verbatim from original Plan 05 Task 2.
       - **`ui.ts`** — minimal currentWeekStart store.
       - **`sync.ts`** — online + pendingMutations + lastSyncedAt store.

       (Verbatim code from original Plan 05 Task 2.)
  </action>
  <verify>
    <automated>cd frontend &amp;&amp; pnpm typecheck &amp;&amp; pnpm lint --max-warnings=0 &amp;&amp; grep -q "Buongiorno" src/i18n/copy.it.ts &amp;&amp; grep -q "Intl.NumberFormat('it-IT')" src/lib/format.ts &amp;&amp; grep -q "Intl.Collator('it')" src/lib/format.ts</automated>
  </verify>
  <acceptance_criteria>
    - File `frontend/src/i18n/copy.it.ts` contains literal `Buongiorno, {nome}` AND `Carica piano` AND `Pesata di oggi` AND `Nuova versione disponibile` AND `as const`
    - File `frontend/src/i18n/copy.it.ts` exports keys: `auth`, `invite`, `pwa`, `sync`, `ai`, `errors`, `appBar`, `today`, `weight`, `workout`, `plans`
    - File `frontend/src/lib/format.ts` contains literal `Intl.NumberFormat('it-IT')` AND `Intl.Collator('it')` AND `parseItalianDecimal` AND `export const nfc`
    - File `frontend/src/hooks/useReducedMotion.ts` contains literal `prefers-reduced-motion: reduce`
    - File `frontend/src/hooks/useOnline.ts` contains literal `navigator.onLine`
    - File `frontend/src/stores/theme.ts` contains literal `applyTheme` AND `data-theme` AND `persist(`
    - File `frontend/src/stores/sync.ts` contains literal `pendingMutations` AND `lastSyncedAt`
    - Command `cd frontend && pnpm typecheck` exits 0
    - Command `cd frontend && pnpm lint --max-warnings=0` exits 0
  </acceptance_criteria>
  <done>copy.it.ts contains every UI-SPEC §7.2 Italian string. lib/format.ts ships full Italian Intl helpers. Hooks (useReducedMotion, useOnline, useMediaQuery, useTheme, useToast, useDebounce) ready. Zustand stores (theme persisted, ui, sync) ready for Plans 03/06/07.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Test infrastructure — Vitest + Playwright + axe + visual diff + Lighthouse CI + smoke + a11y + visual specs + motion test</name>
  <files>frontend/vitest.config.ts, frontend/playwright.config.ts, frontend/lighthouserc.json, frontend/src/test/setup.ts, frontend/tests/e2e/smoke.spec.ts, frontend/tests/e2e/a11y.spec.ts, frontend/tests/visual/light.spec.ts, frontend/tests/visual/dark.spec.ts, frontend/src/styles/__tests__/motion.test.ts</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md (Pitfall #12 axe-core CI on built dist, Validation Architecture)
    - .planning/phases/01-foundation/01-UI-SPEC.md (§9 Accessibility Gates)
    - .planning/phases/01-foundation/01-VALIDATION.md (Sampling Rate, Wave 0 Requirements)
    - frontend/package.json (verify test deps installed by 05a; if missing: `pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @playwright/test @axe-core/playwright @lhci/cli`)
  </read_first>
  <action>
    1. **Install test deps** if not already pulled in by Plan 05a:
       ```bash
       cd frontend
       pnpm add -D vitest @testing-library/react @testing-library/jest-dom \
         @testing-library/user-event jsdom \
         @playwright/test @axe-core/playwright @lhci/cli
       ```

    2. **`frontend/vitest.config.ts`** — jsdom environment with theme tokens injected (verbatim from original Plan 05 Task 2).

    3. **`frontend/src/test/setup.ts`** — testing-library/jest-dom + matchMedia mock + theme tokens injected via inline style tag (verbatim from original Plan 05 Task 2).

    4. **`frontend/playwright.config.ts`** — projects: chromium-light, chromium-dark, mobile-iphone-13, axe (Pitfall #12 — runs against `pnpm preview` of built dist):
       ```typescript
       import { defineConfig, devices } from '@playwright/test';

       export default defineConfig({
         testDir: './tests',
         fullyParallel: true,
         retries: process.env.CI ? 2 : 0,
         use: {
           baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:4173',
           trace: 'on-first-retry',
           screenshot: 'only-on-failure',
           contextOptions: { reducedMotion: 'reduce' },
         },
         webServer: {
           command: 'pnpm preview --port 4173',
           port: 4173,
           timeout: 60_000,
           reuseExistingServer: !process.env.CI,
         },
         projects: [
           { name: 'axe', testMatch: /a11y\.spec\.ts/, use: { ...devices['Desktop Chrome'] } },
           { name: 'visual-light', testMatch: /visual\/light\.spec\.ts/,
             use: { ...devices['Desktop Chrome'], colorScheme: 'light' } },
           { name: 'visual-dark', testMatch: /visual\/dark\.spec\.ts/,
             use: { ...devices['Desktop Chrome'], colorScheme: 'dark' } },
           { name: 'iphone-13', testMatch: /e2e\/.*\.spec\.ts/, use: { ...devices['iPhone 13'] } },
           { name: 'chromium', testMatch: /e2e\/.*\.spec\.ts/, use: { ...devices['Desktop Chrome'] } },
         ],
         expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.01 } },
       });
       ```

    5. **`frontend/lighthouserc.json`** — Lighthouse CI thresholds (UI-11 ≥95 a11y, UI-09 PWA = 100):
       ```json
       {
         "ci": {
           "collect": {
             "url": ["http://localhost:4173/login"],
             "startServerCommand": "pnpm preview --port 4173",
             "startServerReadyPattern": "Local",
             "settings": { "preset": "desktop" }
           },
           "assert": {
             "assertions": {
               "categories:accessibility": ["error", { "minScore": 0.95 }],
               "categories:pwa": ["error", { "minScore": 1.0 }]
             }
           },
           "upload": { "target": "temporary-public-storage" }
         }
       }
       ```

    6. **`frontend/tests/e2e/smoke.spec.ts`** — basic boot test (verbatim from original Plan 05 Task 2).

    7. **`frontend/tests/e2e/a11y.spec.ts`** — axe-core CI gate (UI-10) — verbatim from original Plan 05 Task 2.

    8. **`frontend/tests/visual/light.spec.ts`** + **`frontend/tests/visual/dark.spec.ts`** — split the visual diff suite per color scheme (matches the `visual-light` / `visual-dark` Playwright projects):
       ```typescript
       // light.spec.ts
       import { test, expect } from '@playwright/test';
       const ROUTES = ['/login', '/today', '/piano', '/impostazioni'];
       for (const route of ROUTES) {
         test(`visual-light: ${route}`, async ({ page }) => {
           await page.goto(route);
           await page.waitForLoadState('networkidle');
           await expect(page).toHaveScreenshot(`light${route.replace(/\//g, '_') || '_root'}.png`, {
             maxDiffPixelRatio: 0.02,
             animations: 'disabled',
           });
         });
       }

       // dark.spec.ts (same routes, dark color-scheme — applied via Playwright project use.colorScheme: 'dark')
       import { test, expect } from '@playwright/test';
       const ROUTES = ['/login', '/today', '/piano', '/impostazioni'];
       for (const route of ROUTES) {
         test(`visual-dark: ${route}`, async ({ page }) => {
           await page.goto(route);
           await page.waitForLoadState('networkidle');
           await expect(page).toHaveScreenshot(`dark${route.replace(/\//g, '_') || '_root'}.png`, {
             maxDiffPixelRatio: 0.02,
             animations: 'disabled',
           });
         });
       }
       ```

    9. **`frontend/src/styles/__tests__/motion.test.ts`** — verify motion budget tokens + reduced-motion behavior (verbatim from original Plan 05 Task 2).

    Run: `pnpm vitest run` (unit), `pnpm exec playwright install --with-deps chromium`, `pnpm build && pnpm exec playwright test --project=chromium --grep="boots"` (smoke).
  </action>
  <verify>
    <automated>cd frontend &amp;&amp; pnpm vitest run src/styles/__tests__/motion.test.ts &amp;&amp; pnpm typecheck &amp;&amp; pnpm exec playwright install --with-deps chromium &amp;&amp; pnpm build</automated>
  </verify>
  <acceptance_criteria>
    - File `frontend/playwright.config.ts` contains literal `colorScheme: 'light'` AND `colorScheme: 'dark'` AND `webServer:` AND `pnpm preview --port 4173`
    - File `frontend/lighthouserc.json` contains literal `categories:accessibility` AND `0.95` AND `categories:pwa` AND `1.0`
    - File `frontend/src/test/setup.ts` contains literal `matchMedia` mock AND `--motion-scale: 1`
    - File `frontend/vitest.config.ts` contains literal `environment: 'jsdom'`
    - File `frontend/tests/e2e/a11y.spec.ts` contains literal `AxeBuilder` AND `wcag2aa`
    - File `frontend/tests/visual/light.spec.ts` contains literal `toHaveScreenshot`
    - File `frontend/tests/visual/dark.spec.ts` contains literal `toHaveScreenshot`
    - Command `cd frontend && pnpm vitest run src/styles/__tests__/motion.test.ts` exits 0
    - Command `cd frontend && pnpm exec playwright install --with-deps chromium` exits 0
    - Command `cd frontend && pnpm build` exits 0
  </acceptance_criteria>
  <done>Test infrastructure complete: Vitest jsdom unit tests, Playwright with axe + visual-light/dark + iphone-13 + chromium projects, Lighthouse CI thresholds locked. Smoke + a11y + visual specs in place. CI workflows from Plan 01 will execute these.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| User input -> form | UI-15 mandates `role="alert"` + icon + Italian copy + non-color signal — enforced via copy.it.ts shapes |
| copy.it.ts -> all UI surfaces | FND-09 — single source of truth; ESLint custom rule (Plan 05a) bans hardcoded literals |

## STRIDE Threat Register (Plan 05b scope)

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-A11Y-01 | Repudiation / Denial of Service (UX) | Accessibility regression breaks Phase 1 pause gate | mitigate | axe-core CI gate fails PR on `<4.5:1` body / `<3:1` large/icon (UI-10); Lighthouse a11y >=95 enforced via `lighthouserc.json` (UI-11); dark-mode visual diff per route (UI-12); per-route a11y test in `tests/e2e/a11y.spec.ts` covering /login /register /today /piano /storico /impostazioni |
| T-MOTION-01 | DoS (UX) | Animations not respecting `prefers-reduced-motion` | mitigate | `--motion-scale: 0` set globally via `@media (prefers-reduced-motion: reduce)` in `theme.css` (Plan 05a); CSS rule sets `animation-duration: 0ms !important` and `transition-duration: 0ms !important` on all elements; `useReducedMotion` hook (this plan) exported for component-level branching; `motion.test.ts` (this plan) verifies token state under jsdom |

</threat_model>

<verification>
End-of-plan checks:

```bash
cd frontend
pnpm install
pnpm typecheck
pnpm build  # produces dist/ (Plan 05a)

# Unit tests
pnpm vitest run

# Playwright (after build)
pnpm exec playwright install --with-deps chromium
pnpm exec playwright test --project=chromium --grep="boots"  # smoke
pnpm exec playwright test --project=axe                       # a11y
pnpm exec playwright test --project=visual-light --project=visual-dark  # visual baseline

# Lighthouse (against built dist)
pnpm test:lighthouse-pwa  # asserts a11y >=95 + PWA = 100
```
</verification>

<success_criteria>
- All Task 1 + Task 2 acceptance criteria met
- `copy.it.ts` contains every UI-SPEC §7.2 string verbatim (~80 keys)
- `lib/format.ts` ships `Intl.NumberFormat('it-IT')` + `Intl.Collator('it')` + `parseItalianDecimal`
- `prefers-reduced-motion: reduce` correctly sets `--motion-scale: 0` (motion.test.ts green)
- `pnpm test:axe` runs against built dist with 0 violations
- `pnpm test:visual` produces baseline screenshots for light + dark
- `pnpm test:lighthouse-pwa` returns a11y ≥95 + PWA = 100 (PWA score may require Plan 06 SW landing — flag for Plan 06 if 100 not yet achievable)
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/01-05b-SUMMARY.md` capturing:
- Final test infrastructure summary (Vitest config, Playwright projects, Lighthouse thresholds)
- Initial Lighthouse scores from first run (a11y, PWA, performance)
- Initial visual diff baseline screenshot count (per route × per color scheme)
- copy.it.ts string count (must match UI-SPEC §7.2)
</output>
