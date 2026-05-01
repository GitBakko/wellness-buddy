---
phase: 01-foundation
plan: 05a
subsystem: frontend-skeleton-tokens
tags: [vite, react19, tailwind4, theme-tokens, shadcn, eslint, oklch, dark-mode, motion-budget, pwa-icons]
requires:
  - "Plan 01-01 monorepo scaffold (pnpm workspace, frontend package skeleton, ESLint stub, Prettier, Husky)"
provides:
  - "Vite 7 + React 19.2 + TypeScript 5.9 strict build pipeline producing dist/ with hashed assets"
  - "Tailwind 4 @theme block (UI-SPEC §12 verbatim) — full token foundation every later UI plan inherits"
  - "OKLCH light + dark palettes with explicit dark variants (warm-coral 50-900, leaf-green, neutrals 50-950, semantic AA-verified)"
  - "Typography 4 base sizes (caption/base/heading/display) + 1 escape hatch (display-serif for /today greeting)"
  - "Motion budget tokens (instant 80ms / fast 150ms / base 250ms / slow 400ms / celebration 800ms HARD MAX) + ease-out-soft / ease-spring"
  - "Dark mode dual-source: @media prefers-color-scheme + :root[data-theme=dark] manual override (Pitfall #7)"
  - "@custom-variant dark wires manual data-theme toggle to dark:* utilities"
  - "OKLCH HSL fallback via @supports for Safari < 16.4 (Pitfall #6) + boot-time class set in index.html"
  - "prefers-reduced-motion → --motion-scale: 0 honored by Button/Checkbox/RadioGroup tap-scale (UI-05)"
  - "shadcn/ui components.json points to theme.css + cn.ts (Pitfall #1 fix)"
  - "17 shadcn primitives customized to consume @theme tokens (UI-03 explicit rejection of vanilla)"
  - "Button min-h-11 (UI-06 44px touch target) + active:scale-[0.97] tap microinteraction (UI-04 #6)"
  - "FormField error stack: role=alert + AlertCircle icon + Italian-ready (UI-15 color-blind safety)"
  - "ESLint 9 flat config bans hex outside theme.css/globals.css via no-restricted-syntax (Pitfall #10)"
  - "Prettier with prettier-plugin-tailwindcss for class ordering"
  - "App shell skeleton: main.tsx + App.tsx + router.tsx (createBrowserRouter, 8 lazy routes)"
  - "TanStack Query client (staleTime 30s, retry 1) — Plan 06 wires Dexie persister"
  - "4 PWA icon placeholders (192/512/maskable-512/apple-touch-180) — Plan 08 ships final"
  - "version.json placeholder ({version, build_hash}) — Plan 06 build wires real git SHA"
  - "Sonner Toaster customized to brand palette with success/error/warning border-left variants"
affects:
  - "All Wave 3+ plans (auth pages, parser, /today, etc.) — every UI surface inherits @theme tokens via CSS variables"
  - "Plan 05b (i18n + format helpers + hooks + Zustand stores + test infra) — depends on theme.css + cn.ts existence"
  - "Plan 06 (PWA + SW) — wires vite-plugin-pwa onto this Vite config; overwrites version.json with real build_hash"
  - "Plan 07 (/today + weight + workout pages) — replaces page placeholders with real components"
  - "Plan 03 (auth) — replaces Login/Register/PersistStorageWelcome placeholders"
  - "Plan 04 (plan upload + parser) — replaces Plans page placeholder"
  - "Plan 08 (tone-calibration mockups + final icons) — replaces 4 placeholder PNGs"
tech-stack:
  added:
    - "react@19.2.5"
    - "react-dom@19.2.5"
    - "react-router@7.14.2"
    - "vite@7.3.2"
    - "@vitejs/plugin-react@5.2.0"
    - "tailwindcss@4.2.4"
    - "@tailwindcss/vite@4.2.4"
    - "tailwindcss-animate@1.0.7"
    - "typescript@5.9.3"
    - "typescript-eslint@8.59.1"
    - "eslint@9.39.4 + @eslint/js@9.39.4"
    - "eslint-plugin-react@7.37.5"
    - "eslint-plugin-react-hooks@7.1.1"
    - "globals@17.5.0"
    - "@tanstack/react-query@5.100.7"
    - "@tanstack/query-sync-storage-persister@5.100.7"
    - "zustand@5.0.12"
    - "dexie@4.4.2"
    - "class-variance-authority@0.7.1 + clsx@2.1.1 + tailwind-merge@3.5.0"
    - "@radix-ui/react-{checkbox,dialog,dropdown-menu,label,popover,radio-group,select,slot,switch,tabs,toggle}"
    - "lucide-react@1.14.0"
    - "@fontsource-variable/geist@5.2.8 + @fontsource-variable/geist-mono@5.2.7 + @fontsource/instrument-serif@5.2.5"
    - "motion@12.38.0"
    - "react-hook-form@7.74.0 + @hookform/resolvers@5.2.2 + zod@4.4.1"
    - "sonner@2.0.7"
    - "recharts@3.8.1 + date-fns@4.1.0 + react-day-picker@9.14.0"
    - "react-markdown@10.1.0 + remark-gfm@4.0.1"
    - "vite-plugin-pwa@1.2.0 + workbox-window@7.4.0 (installed; Plan 06 wires)"
    - "prettier@3.8.3 + prettier-plugin-tailwindcss@0.8.0"
  patterns:
    - "Tailwind 4 @theme directive (CSS-first config) — `@import 'tailwindcss'; @theme { … }` (Pattern 1)"
    - "Dark mode dual-source: @media + :root[data-theme=dark] mirror + @custom-variant dark (Pitfall #7)"
    - "OKLCH HSL fallback via @supports not(color: oklch(0 0 0)) (Pitfall #6)"
    - "shadcn/ui v4 components.json points `tailwind.css` to `src/styles/theme.css` not config.ts (Pitfall #1)"
    - "All shadcn primitives consume @theme tokens via `var(--color-*)` — UI-03 customization mandatory"
    - "Tap microinteraction shared utility: `active:scale-[calc(1-0.03*var(--motion-scale))]` (Button/Checkbox/RadioGroup)"
    - "`--motion-scale: 1` default → 0 under prefers-reduced-motion → tap scale becomes no-op"
    - "Button min-h-11 + svg size-5 default + 6 variants (primary/secondary/ghost/destructive/link/outline) via cva"
    - "Form: react-hook-form Controller + FormField context + FormMessage with role=alert + AlertCircle (UI-15)"
    - "Toaster custom classNames map sonner to @theme tokens (border-left for success/error/warning)"
    - "react-router v7 createBrowserRouter with `lazy: async () => ({ Component: (await import(...)).default })` per route"
    - "Path alias @/* → ./src/* in tsconfig + vite.config (shadcn convention + cleaner imports)"
    - "Geist via @fontsource-variable (Vite-compatible) instead of `geist` npm pkg (Next.js-only)"
    - "Hand-rolled Node script generates 4 PWA icons (zlib + crc32 only — zero runtime deps for CI determinism)"
key-files:
  created:
    - frontend/vite.config.ts
    - frontend/tsconfig.json
    - frontend/tsconfig.app.json
    - frontend/tsconfig.node.json
    - frontend/index.html
    - frontend/components.json
    - frontend/src/styles/theme.css
    - frontend/src/styles/globals.css
    - frontend/src/lib/cn.ts
    - frontend/src/lib/queryClient.ts
    - frontend/src/main.tsx
    - frontend/src/App.tsx
    - frontend/src/router.tsx
    - frontend/src/vite-env.d.ts
    - frontend/src/components/ui/button.tsx
    - frontend/src/components/ui/input.tsx
    - frontend/src/components/ui/textarea.tsx
    - frontend/src/components/ui/label.tsx
    - frontend/src/components/ui/checkbox.tsx
    - frontend/src/components/ui/switch.tsx
    - frontend/src/components/ui/select.tsx
    - frontend/src/components/ui/radio-group.tsx
    - frontend/src/components/ui/dialog.tsx
    - frontend/src/components/ui/sheet.tsx
    - frontend/src/components/ui/dropdown-menu.tsx
    - frontend/src/components/ui/form.tsx
    - frontend/src/components/ui/card.tsx
    - frontend/src/components/ui/tabs.tsx
    - frontend/src/components/ui/calendar.tsx
    - frontend/src/components/ui/sonner.tsx
    - frontend/src/components/ui/skeleton.tsx
    - frontend/src/components/auth/PersistStorageWelcome.tsx
    - frontend/src/pages/Login.tsx
    - frontend/src/pages/Register.tsx
    - frontend/src/pages/Today.tsx
    - frontend/src/pages/Plans.tsx
    - frontend/src/pages/History.tsx
    - frontend/src/pages/Settings.tsx
    - frontend/public/icons/icon-192.png
    - frontend/public/icons/icon-512.png
    - frontend/public/icons/icon-maskable-512.png
    - frontend/public/icons/apple-touch-icon-180.png
    - frontend/public/version.json
    - scripts/generate-pwa-placeholder-icons.mjs
  modified:
    - frontend/package.json
    - frontend/eslint.config.js
    - lint-staged.config.js
    - pnpm-lock.yaml
decisions:
  - "Vite 7.3.2 over Vite 8 because vite-plugin-pwa@1.2.0 (Plan 06 dep) caps peer at vite^7. Plan 06 will use the installed pwa plugin; upgrading to Vite 8 deferred to Phase 4 re-evaluation (STATE Q9)."
  - "Replaced `geist` npm pkg with @fontsource-variable/geist + @fontsource/instrument-serif. Original pkg only exports Next.js's localFont() and won't work in Vite (Rule 3 deviation). Same fonts shipped, font-family names updated in @theme to 'Geist Variable' / 'Geist Mono Variable' with original 'Geist Sans' / 'Geist Mono' kept as fallbacks for forward-compat."
  - "Authored 17 shadcn primitives inline instead of `pnpm dlx shadcn add` because the CLI requires interactive prompts no agent runtime can answer (Rule 3 deviation). UI-03 mandates customization regardless, so net effect identical — every primitive consumes @theme tokens via `var(--color-*)`."
  - "ESLint 9 (not 10) because eslint-plugin-react peers cap at ^9.7. ESLint 10 + React plugin combo not yet GA-stable as of 2026-05-01."
  - "TypeScript 5.9.3 (not 5.6) because typescript-eslint@8 peer requires <6.1 and 5.9 is the latest within that window. tsconfig still uses moduleResolution: bundler + verbatimModuleSyntax."
  - "Composite tsconfig split (tsconfig.app.json for src + tsconfig.node.json for vite.config.ts) — modern Vite 7 convention, enables incremental builds via tsBuildInfoFile."
  - "Hex-character literals in index.html manifest theme_color (#FAF9F6 / #1B1F26) explicitly preserved — UI-SPEC §10.4 requires raw hex for `<meta name=theme-color>` (browsers don't accept oklch in this meta). ESLint hex-ban scoped to src/**/*.{ts,tsx} only; theme.css and globals.css explicitly excluded; index.html not in eslint scope."
  - "Page modules (Login/Register/Today/Plans/History/Settings + PersistStorageWelcome) shipped as placeholders so router lazy imports resolve. Plans 03/04/06/07 own each one."
  - "PWA icons generated by zero-dep Node script (built-in zlib + crc32 only) so CI builds are deterministic without sharp/imagemagick. Output is solid-coral 'plus-mark' placeholder; Plan 08 ships final brand mark."
  - "lint-staged updated to use `eslint --no-warn-ignored` so config files (vite.config.ts, .prettierrc.cjs) co-staged with src changes don't fail max-warnings=0 due to ignore-pattern warnings."
metrics:
  duration: "~25 minutes"
  completed: "2026-05-01"
  tasks_completed: 2
  total_tasks: 2
  files_created: 42
  files_modified: 4
  commits: 2
  theme_tokens: 160         # --var declarations across @theme + dark + manual override + alias maps
  shadcn_primitives: 17
---

# Phase 1 Plan 05a: Frontend Skeleton + Vite + Tailwind 4 @theme + shadcn/ui 17 primitives Summary

WIN REQUISITE UI/UX foundation landed: Vite 7 + React 19 + TypeScript 5.9 strict build pipeline with the Tailwind 4 `@theme` token block as single source of truth. 17 shadcn primitives customized to consume `var(--color-*)` tokens, ESLint hex-ban enforced outside `theme.css`, dark mode first-class via `@media` + `:root[data-theme=dark]` mirror, motion budget honored by `--motion-scale` reduced-motion gate, and 4 PWA icon placeholders shipped — every Wave 3+ surface now inherits a locked design contract.

## What this plan delivers

The Tailwind 4 `@theme` block is a contract that every later phase consumes verbatim. `theme.css` declares 13 spacing tokens, 6 radius tokens, 4 base typography sizes + 1 escape hatch, full OKLCH light + dark palettes (warm-coral 50-900, leaf-green, neutrals 50-950, semantic success/warning/destructive AA-verified per UI-SPEC §4.2), 5 motion durations + 2 easings, plus shadcn alias mappings (`--color-background`, `--color-primary`, etc.) so the 17 customized primitives (Button/Input/Textarea/Label/Checkbox/Switch/Select/RadioGroup/Dialog/Sheet/DropdownMenu/Form/Card/Tabs/Calendar/Sonner/Skeleton) consume brand tokens by default with zero hardcoded hex.

Dark mode is dual-sourced: `@media (prefers-color-scheme: dark)` for system preference (only fires when user hasn't explicitly chosen `data-theme="light"`) plus an explicit `:root[data-theme="dark"]` mirror for the manual ThemeToggle (Settings page, Plan 07). The two branches are kept identical to avoid Pitfall #7 drift. `@custom-variant dark` makes `dark:bg-…` Tailwind utilities respect the manual toggle in addition to system preference.

Motion is gated by `--motion-scale`: default `1`, set to `0` under `@media (prefers-reduced-motion: reduce)`. The Button/Checkbox/RadioGroup tap microinteraction uses `active:scale-[calc(1-0.03*var(--motion-scale))]` so reduced-motion users see the underlying scale collapse to a no-op (UI-05). Every duration is bounded by the budget (HARD MAX 250ms for micro-transitions, 800ms for celebrations, 80ms for tap).

Build pipeline: `pnpm typecheck && pnpm build && pnpm lint --max-warnings=0` all green. `dist/` produced with hashed assets (`assets/index-<hash>.js` + `index-<hash>.css` + 7 lazy chunks for routes + 6 woff2 font files). 102 modules transformed in ~1.6s. Bundle: 344 kB main JS (108 kB gzip), 42 kB CSS (8 kB gzip). Hand-rolled Node script generates 4 placeholder PWA icons (solid coral) using only Node's built-in `zlib` + custom CRC32 — zero runtime deps for deterministic CI builds. Plan 08 replaces with final brand marks after tone-calibration mockup review.

## Hardlinks for downstream plans

- **Plan 05b** consumes `frontend/src/lib/cn.ts` and the `@theme` tokens via `var(--…)` references in i18n/format helpers.
- **Plan 06** wires `vite-plugin-pwa@1.2.0` (already installed) into `vite.config.ts` and overwrites `public/version.json` with real git SHA at build time.
- **Plan 07** replaces 4 page placeholders (Today/Plans/History/Settings) and uses Card/Sheet/Dialog/Skeleton + Recharts via tokens for `/today` + weight chart + workout form.
- **Plan 03** replaces Login/Register/PersistStorageWelcome placeholders with real auth flows.
- **Plan 04** replaces Plans placeholder with PlanUploadDropzone + PlanDiffView.
- **Plan 08** replaces 4 PWA icon placeholders + ships final tone calibration mockups using all primitives end-to-end.

## Verification — full plan

```bash
cd frontend
pnpm typecheck       # exits 0
pnpm build           # produces dist/ with hashed assets
pnpm lint --max-warnings=0   # exits 0

# Token coverage check (no hardcoded hex outside theme.css/globals.css)
grep -RnP '#[0-9a-fA-F]{3,8}' frontend/src --include='*.tsx' --include='*.ts'
# returns 0 matches
```

All three exit 0. Token coverage check returns 0 hex literals across `frontend/src/**`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Vite 7.3.2 instead of Vite 8 GA**
- **Found during:** Task 1 dep version verification
- **Issue:** Plan declared `vite@^7` but Vite 8.0.10 was already GA at 2026-05-01. However, `vite-plugin-pwa@1.2.0` (Plan 06 dep, installed in Task 1) caps peer at `vite^7`.
- **Fix:** Locked Vite 7.3.2 (latest 7.x). Plan 06 will use the installed pwa plugin without contention. STATE Q9 already declared "Vite 7 hold for Sprint 1 stability, re-evaluate Sprint 4" — this is a confirmation of that decision, not a new one.
- **Files modified:** frontend/package.json
- **Commit:** fcd0795

**2. [Rule 3 - Blocking] @fontsource-variable/geist replacing `geist` npm package**
- **Found during:** Task 2 main.tsx implementation
- **Issue:** The `geist` npm package (locked in plan as a dep) only exports `geist/font/sans` and `geist/font/mono` via Next.js's `next/font/local` helper. It throws on import in plain Vite/React.
- **Fix:** Removed `geist` package; added `@fontsource-variable/geist` + `@fontsource-variable/geist-mono` + `@fontsource/instrument-serif` (latest Variable + 400 weight). Same fonts loaded via standard `@font-face` declarations. Updated `--font-sans` / `--font-mono` / `--font-display` in `theme.css` to use the actual font-family names (`'Geist Variable'`, `'Geist Mono Variable'`) with original `'Geist Sans'` / `'Geist Mono'` aliases kept as fallbacks so future swaps stay token-stable.
- **Files modified:** frontend/package.json, frontend/src/main.tsx, frontend/src/styles/theme.css
- **Commit:** fcd0795 (theme.css), e7bf9a5 (main.tsx + package change finalised)

**3. [Rule 3 - Blocking] 17 shadcn primitives authored inline instead of CLI install**
- **Found during:** Task 1 step 10–13 ("shadcn/ui CLI init")
- **Issue:** `pnpm dlx shadcn@latest init` and subsequent `add` commands require interactive TTY prompts (style, base color, CSS variables, components dir, utils path, RSC, tailwind.config). Agent runtime cannot answer interactive prompts.
- **Fix:** Authored `components.json` directly per RESEARCH Pattern 2 (locked verbatim). Authored each of the 17 primitives directly with `cn()` helper, Radix primitives, and brand-token classNames. UI-03 mandates customization after `add` regardless, so the end state is identical to the CLI path + manual edits — minus a dependency on a prompt-driven tool. Each primitive imports from `@/lib/cn` and uses `var(--color-*)` exclusively (zero hex).
- **Files created:** frontend/components.json + 17 ui/*.tsx files
- **Commit:** fcd0795

**4. [Rule 3 - Blocking] ESLint 9.39.4 (not ESLint 10)**
- **Found during:** Task 1 dep verification
- **Issue:** `eslint-plugin-react@7.37.5` peer caps at `eslint^9.7`. ESLint 10 GA but the React plugin doesn't yet declare ESLint 10 in its peer range.
- **Fix:** Locked `eslint@9.39.4` + `@eslint/js@9.39.4`. `typescript-eslint@8.59.1` and `eslint-plugin-react-hooks@7.1.1` already accept ESLint 9.
- **Files modified:** frontend/package.json
- **Commit:** fcd0795

**5. [Rule 3 - Blocking] react-day-picker v9 Calendar component shape**
- **Found during:** Typecheck after Calendar primitive
- **Issue:** Plan/RESEARCH wrote `components: { IconLeft, IconRight }` but react-day-picker v9 renamed the slot to `Chevron({ orientation })`.
- **Fix:** Updated `Calendar.tsx` to use the new shape. Same chevron icons rendered, same a11y semantics.
- **Files modified:** frontend/src/components/ui/calendar.tsx
- **Commit:** fcd0795

**6. [Rule 3 - Blocking] lint-staged --no-warn-ignored**
- **Found during:** First Task 1 commit attempt — pre-commit hook failed
- **Issue:** lint-staged passes ALL staged files (including `vite.config.ts`) to ESLint. ESLint emits a warning when it skips an explicitly-ignored file, and `--max-warnings=0` then fails the hook.
- **Fix:** Updated `lint-staged.config.js` to call `eslint --fix --max-warnings=0 --no-warn-ignored` and scope to `frontend/src/**/*.{ts,tsx}` only (skipping config files entirely so ESLint never sees ignored files in the first place).
- **Files modified:** lint-staged.config.js
- **Commit:** fcd0795

**7. [Rule 2 - Critical] CSS module type declarations**
- **Found during:** Task 2 typecheck — TS2307 on every CSS import
- **Issue:** TypeScript strict mode rejects untyped CSS module imports.
- **Fix:** Added `frontend/src/vite-env.d.ts` with `<reference types="vite/client" />` and `declare module '*.css';` declarations. Standard Vite practice.
- **Files created:** frontend/src/vite-env.d.ts
- **Commit:** fcd0795

### Authentication gates

None — this plan has no auth surface.

## Threat Flags

None. Plan 05a touches build pipeline and design tokens only — no new auth/network/file-access surface beyond what's already in the threat register (T-XSS-01 token tampering and T-A11Y-01 tap-target both fully mitigated as planned).

## Self-Check: PASSED

Verified files exist on disk and commits exist in git history.

```
FOUND: frontend/src/styles/theme.css
FOUND: frontend/components.json
FOUND: frontend/src/components/ui/button.tsx
FOUND: frontend/src/components/ui/dialog.tsx
FOUND: frontend/src/components/ui/sonner.tsx
FOUND: frontend/src/main.tsx
FOUND: frontend/src/App.tsx
FOUND: frontend/src/router.tsx
FOUND: frontend/public/icons/icon-192.png
FOUND: frontend/public/icons/icon-512.png
FOUND: frontend/public/icons/icon-maskable-512.png
FOUND: frontend/public/icons/apple-touch-icon-180.png
FOUND: frontend/public/version.json
FOUND commit fcd0795 (Task 1)
FOUND commit e7bf9a5 (Task 2)
```

Acceptance literals verified:
- `@theme` in theme.css (3 occurrences — main, dark @media, comment refs)
- `@custom-variant dark` in theme.css
- `oklch(63% 0.165 28)` (coral-500 light) in theme.css
- `--text-display-serif: 2.25rem` in theme.css
- `--motion-scale: 1` in theme.css
- `:root[data-theme="dark"]` in theme.css
- `"css": "src/styles/theme.css"` in components.json
- `"baseColor": "neutral"` in components.json
- 17 ui/*.tsx primitives present
- `no-restricted-syntax` + hex regex in eslint.config.js
- `prettier-plugin-tailwindcss` in .prettierrc.cjs
- `oklch(50% 0 0)` + `apple-mobile-web-app-status-bar-style` in index.html
- `import './styles/theme.css'` in main.tsx
- `RouterProvider router={router}` in main.tsx
- `createBrowserRouter` + `lazy: async () =>` in router.tsx
- `<Outlet />` in App.tsx
- `staleTime: 30_000` in queryClient.ts

Build artifacts in `frontend/dist/`:
```
dist/index.html (1.61 kB)
dist/version.json
dist/icons/{icon-192,icon-512,icon-maskable-512,apple-touch-icon-180}.png
dist/assets/index-<hash>.js (344 kB → 108 kB gzip)
dist/assets/index-<hash>.css (42 kB → 8 kB gzip)
dist/assets/{Login,Register,Today,Plans,History,Settings,PersistStorageWelcome}-<hash>.js (lazy route chunks)
dist/assets/{geist*,geist-mono*,instrument-serif*}.woff2 (6 font files)
```
