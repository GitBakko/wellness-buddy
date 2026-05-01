---
phase: 01-foundation
plan: 05a
type: execute
wave: 2
depends_on: [01]
files_modified:
  - frontend/package.json
  - frontend/vite.config.ts
  - frontend/tsconfig.json
  - frontend/tsconfig.node.json
  - frontend/index.html
  - frontend/components.json
  - frontend/eslint.config.js
  - frontend/.prettierrc.cjs
  - frontend/public/icons/icon-192.png
  - frontend/public/icons/icon-512.png
  - frontend/public/icons/icon-maskable-512.png
  - frontend/public/icons/apple-touch-icon-180.png
  - frontend/public/version.json
  - frontend/src/main.tsx
  - frontend/src/App.tsx
  - frontend/src/router.tsx
  - frontend/src/styles/theme.css
  - frontend/src/styles/globals.css
  - frontend/src/lib/cn.ts
  - frontend/src/lib/queryClient.ts
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
autonomous: true
requirements: [FND-04, UI-01, UI-02, UI-03, UI-07, UI-08, UI-09]
must_haves:
  truths:
    - "Vite + React 19 + TypeScript 5.6 + TailwindCSS 4 builds cleanly"
    - "Tailwind 4 @theme block declares all Phase 1 design tokens (spacing/radius/typography/colors light+dark/motion)"
    - "shadcn/ui CLI initialized; 17 primitive components installed and customized to consume @theme tokens (no hardcoded shadcn colors)"
    - "Dark mode via @media (prefers-color-scheme: dark) + manual data-theme override both work"
    - "@custom-variant dark configured so dark:* utilities respect manual data-theme toggle"
    - "OKLCH baseline check + HSL fallback shipped via @supports (Pitfall #6)"
    - "ESLint 9 flat config bans hardcoded hex outside theme.css/globals.css (no-restricted-syntax rule)"
    - "All 4 PWA icon files present (192/512/maskable-512/apple-touch-180)"
  artifacts:
    - path: "frontend/src/styles/theme.css"
      provides: "All Tailwind 4 @theme design tokens (spacing/radius/font/typography/colors light+dark/motion)"
      contains: "@theme"
    - path: "frontend/components.json"
      provides: "shadcn/ui v4 config pointing CSS to theme.css (Pitfall #1 fix)"
      contains: "src/styles/theme.css"
    - path: "frontend/eslint.config.js"
      provides: "ESLint 9 flat config with no-restricted-syntax hex ban"
      contains: "no-restricted-syntax"
    - path: "frontend/src/lib/cn.ts"
      provides: "clsx + tailwind-merge helper"
      contains: "twMerge"
  key_links:
    - from: "frontend/src/main.tsx"
      to: "frontend/src/styles/theme.css"
      via: "import 'theme.css' before component CSS"
      pattern: "theme.css"
    - from: "frontend/components.json"
      to: "frontend/src/styles/theme.css"
      via: "shadcn CLI tailwind.css points to theme.css"
      pattern: "src/styles/theme.css"
    - from: "frontend/src/styles/theme.css"
      to: "frontend/src/components/ui/*"
      via: "shadcn primitives reference --color-coral-500 etc via cn()"
      pattern: 'var\(--color-'
---

<objective>
Land the WIN REQUISITE UI/UX foundation (split 1 of 2): Vite 7 + React 19 + TypeScript 5.6 + TailwindCSS 4 build pipeline, `@theme` block with ALL design tokens (spacing, radius, font families, typography 4-size + escape hatch, OKLCH light+dark palette, motion budget), shadcn/ui CLI init + 17 customized primitive components, dark mode (media query + manual data-theme), OKLCH baseline check with HSL fallback, app shell skeleton (`main.tsx`, `App.tsx`, `router.tsx`), ESLint 9 flat config + Prettier, 4 PWA icon placeholders, version.json placeholder, lib helpers (cn, queryClient).

The i18n + format helpers + hooks + Zustand stores + test infrastructure (Vitest + Playwright + axe + visual diff + Lighthouse + smoke specs) are owned by Plan 05b, which lands in parallel within Wave 2.

Purpose: This plan is the UI foundation — every Wave 3+ plan (auth pages, parser pages, /today, etc.) inherits @theme tokens via CSS variables. Per Pitfall #1: Tailwind 4 + shadcn/ui v4 setup quirks fixed by setting up `@theme` BEFORE `pnpm dlx shadcn init`.

**Co-modified files with Plan 05b:** none material — 05b only adds new files (no overlap with 05a's file list above). Both plans land within Wave 2 in parallel-friendly fashion.

Output: `pnpm build` succeeds, `dist/` produced with hashed assets. Every Wave 3 plan inherits tokens via CSS variables.
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
@d:/Develop/AI/WellnessBuddy/CLAUDE.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-01-PLAN.md
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Frontend deps install + Vite + TypeScript + Tailwind 4 @theme + shadcn/ui CLI init + 17 primitives + ESLint 9 flat + Prettier</name>
  <files>frontend/package.json, frontend/vite.config.ts, frontend/tsconfig.json, frontend/tsconfig.node.json, frontend/index.html, frontend/components.json, frontend/eslint.config.js, frontend/.prettierrc.cjs, frontend/src/styles/theme.css, frontend/src/styles/globals.css, frontend/src/lib/cn.ts, frontend/src/components/ui/button.tsx, frontend/src/components/ui/input.tsx, frontend/src/components/ui/textarea.tsx, frontend/src/components/ui/label.tsx, frontend/src/components/ui/checkbox.tsx, frontend/src/components/ui/switch.tsx, frontend/src/components/ui/select.tsx, frontend/src/components/ui/radio-group.tsx, frontend/src/components/ui/dialog.tsx, frontend/src/components/ui/sheet.tsx, frontend/src/components/ui/dropdown-menu.tsx, frontend/src/components/ui/form.tsx, frontend/src/components/ui/card.tsx, frontend/src/components/ui/tabs.tsx, frontend/src/components/ui/calendar.tsx, frontend/src/components/ui/sonner.tsx, frontend/src/components/ui/skeleton.tsx</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md ("Frontend Installation" section, Pattern 1 Tailwind 4 @theme verbatim, Pattern 2 shadcn CLI install order)
    - .planning/phases/01-foundation/01-UI-SPEC.md (§1-§7, §12 Final Lock List, §3 typography 4 sizes + escape hatch)
    - .planning/research/PITFALLS.md (#1 Tailwind 4 + shadcn v4 setup, #6 OKLCH baseline)
    - frontend/package.json (Plan 01 manifest skeleton)
  </read_first>
  <action>
    1. **Install all frontend deps** per RESEARCH.md "Frontend Installation":
       ```bash
       cd frontend
       pnpm add react@^19.2 react-dom@^19.2 react-router@^7
       pnpm add zustand@^5 @tanstack/react-query@^5 @tanstack/query-sync-storage-persister
       pnpm add dexie@^4.4
       pnpm add class-variance-authority clsx tailwind-merge tailwindcss-animate
       pnpm add lucide-react geist
       pnpm add @radix-ui/react-dialog @radix-ui/react-dropdown-menu \
         @radix-ui/react-popover @radix-ui/react-tabs @radix-ui/react-toggle \
         @radix-ui/react-select @radix-ui/react-checkbox \
         @radix-ui/react-radio-group @radix-ui/react-switch @radix-ui/react-label \
         @radix-ui/react-slot
       pnpm add motion
       pnpm add react-hook-form zod @hookform/resolvers
       pnpm add sonner
       pnpm add recharts@^3 date-fns@^4 react-day-picker@^9
       pnpm add react-markdown remark-gfm
       pnpm add -D vite@^7 @vitejs/plugin-react @tailwindcss/vite tailwindcss@^4 postcss autoprefixer
       pnpm add -D vite-plugin-pwa workbox-window
       pnpm add -D prettier prettier-plugin-tailwindcss \
         eslint @eslint/js typescript-eslint eslint-plugin-react eslint-plugin-react-hooks
       ```
       (Test deps are added by Plan 05b: vitest, @testing-library/react, @playwright/test, @axe-core/playwright, @lhci/cli, jsdom.)

    2. **`frontend/tsconfig.json`** + **`frontend/tsconfig.node.json`** — strict TS 5.6 with `@/*` path alias (verbatim from original Plan 05 Task 1).

    3. **`frontend/index.html`** — UI-SPEC §10.4 manifest meta + theme color media queries + OKLCH baseline check (Pitfall #6) — verbatim from original Plan 05 Task 1.

    4. **`frontend/vite.config.ts`** — Vite 7 + react + tailwindcss(@4) + alias (Plan 06 adds vite-plugin-pwa) — verbatim from original Plan 05 Task 1.

    5. **`frontend/src/styles/theme.css`** — verbatim from RESEARCH Pattern 1 + UI-SPEC §12 final lock list (full @theme block, including `@custom-variant dark`, OKLCH light + dark palettes, motion tokens, prefers-reduced-motion media query). The full content is committed verbatim — do not abridge.

    6. **`frontend/src/styles/globals.css`** — base reset + OKLCH HSL fallback (Pitfall #6) — verbatim from original Plan 05 Task 1.

    7. **`frontend/src/lib/cn.ts`** — clsx + tailwind-merge helper.

    8. **`frontend/eslint.config.js`** — flat config (D-09, ESLint 9, no-restricted-syntax hex ban) — verbatim from original Plan 01 Task 3 / Plan 05.

    9. **`frontend/.prettierrc.cjs`** — Prettier with prettier-plugin-tailwindcss.

    10. **shadcn/ui CLI init** (Pitfall #1 — set up @theme first, then init):
        ```bash
        test -f src/styles/theme.css
        pnpm dlx shadcn@latest init --yes \
          --style new-york --base-color neutral --css-variables true \
          --components-dir src/components/ui --utils src/lib/cn
        ```

    11. **Verify `frontend/components.json`** matches RESEARCH Pattern 2.

    12. **Install 17 shadcn primitives** in dependency order (Pattern 2):
        ```bash
        pnpm dlx shadcn@latest add button input textarea label checkbox switch select radio-group --yes
        pnpm dlx shadcn@latest add dialog sheet dropdown-menu form card tabs --yes
        pnpm dlx shadcn@latest add calendar sonner skeleton --yes
        ```

    13. **Customize each shadcn primitive** to consume `@theme` tokens (UI-03 explicit rejection of vanilla shadcn colors):
        - Add to `theme.css` `@theme` block: shadcn alias variables (`--background`, `--foreground`, `--card`, `--primary`, etc.) mapped to our brand tokens (verbatim list from original Plan 05 Task 1).
        - Button: add `min-h-11` (44px tap target per UI-06) and `active:scale-[0.97] transition-transform duration-[var(--duration-instant)]`.

    Run `pnpm install` (already deps locked above).
  </action>
  <verify>
    <automated>cd frontend &amp;&amp; pnpm install &amp;&amp; pnpm typecheck &amp;&amp; pnpm build &amp;&amp; pnpm lint --max-warnings=0 &amp;&amp; test -f src/styles/theme.css &amp;&amp; test -f components.json &amp;&amp; test -f src/components/ui/button.tsx &amp;&amp; test -f src/components/ui/dialog.tsx &amp;&amp; test -f src/components/ui/sonner.tsx &amp;&amp; grep -q "@theme" src/styles/theme.css &amp;&amp; grep -q "@custom-variant dark" src/styles/theme.css</automated>
  </verify>
  <acceptance_criteria>
    - File contains literal: `frontend/src/styles/theme.css` -> `@theme` AND `--text-display-serif: 2.25rem` AND `oklch(63% 0.165 28)` (coral-500 light) AND `--motion-scale: 1` AND `@custom-variant dark`
    - File contains literal: `frontend/src/styles/theme.css` -> `@media (prefers-color-scheme: dark)` AND `:root[data-theme="dark"]`
    - File contains literal: `frontend/components.json` -> `"css": "src/styles/theme.css"` AND `"baseColor": "neutral"`
    - All 17 shadcn primitive files exist under `frontend/src/components/ui/`
    - File `frontend/eslint.config.js` contains literal `no-restricted-syntax` AND hex regex
    - File `frontend/.prettierrc.cjs` contains literal `prettier-plugin-tailwindcss`
    - File `frontend/index.html` contains literal `oklch(50% 0 0)` AND `apple-mobile-web-app-status-bar-style`
    - Command `cd frontend && pnpm typecheck` exits 0
    - Command `cd frontend && pnpm build` exits 0 (produces `dist/` with hashed assets + index.html)
    - Command `cd frontend && pnpm lint --max-warnings=0` exits 0
  </acceptance_criteria>
  <done>Vite + React 19 + TypeScript + Tailwind 4 build pipeline + @theme block with all design tokens + shadcn 17 primitives customized + ESLint 9 hex-ban + Prettier configured. `pnpm build` produces `dist/`.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: App shell skeleton (main.tsx + App.tsx + router.tsx) + lib/queryClient + 4 PWA icon placeholders + version.json</name>
  <files>frontend/src/main.tsx, frontend/src/App.tsx, frontend/src/router.tsx, frontend/src/lib/queryClient.ts, frontend/public/icons/icon-192.png, frontend/public/icons/icon-512.png, frontend/public/icons/icon-maskable-512.png, frontend/public/icons/apple-touch-icon-180.png, frontend/public/version.json</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md ("Frontend `main.tsx` entry" code example)
    - .planning/phases/01-foundation/01-UI-SPEC.md (§10.4 manifest meta)
    - frontend/src/styles/theme.css (Task 1 — must import in main.tsx)
  </read_first>
  <action>
    1. **`frontend/src/lib/queryClient.ts`** (TanStack Query — Plan 06 adds Dexie persister):
       ```typescript
       import { QueryClient } from '@tanstack/react-query';

       export const queryClient = new QueryClient({
         defaultOptions: {
           queries: { staleTime: 30_000, refetchOnWindowFocus: true, retry: 1 },
           mutations: { retry: 0 },
         },
       });
       ```

    2. **`frontend/src/main.tsx`** — verbatim from RESEARCH "Frontend `main.tsx` entry":
       ```tsx
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

    3. **`frontend/src/App.tsx`** — placeholder root component:
       ```tsx
       import { Outlet } from 'react-router';
       export default function App() { return <Outlet />; }
       ```

    4. **`frontend/src/router.tsx`** — react-router v7 createBrowserRouter with lazy routes (page modules are placeholder; Plans 03/04/06/07 ship real pages):
       ```tsx
       import { createBrowserRouter, redirect } from 'react-router';
       import App from './App';

       export const router = createBrowserRouter([
         {
           path: '/',
           element: <App />,
           children: [
             { index: true, loader: () => redirect('/today') },
             { path: 'login', lazy: async () => ({ Component: (await import('./pages/Login')).default }) },
             { path: 'register', lazy: async () => ({ Component: (await import('./pages/Register')).default }) },
             { path: 'welcome', lazy: async () => ({ Component: (await import('./components/auth/PersistStorageWelcome')).PersistStorageWelcome }) },
             { path: 'today', lazy: async () => ({ Component: (await import('./pages/Today')).default }) },
             { path: 'piano', lazy: async () => ({ Component: (await import('./pages/Plans')).default }) },
             { path: 'storico', lazy: async () => ({ Component: (await import('./pages/History')).default }) },
             { path: 'impostazioni', lazy: async () => ({ Component: (await import('./pages/Settings')).default }) },
           ],
         },
       ]);
       ```

    5. **Page placeholders** — to keep router lazy imports valid until Plans 03/04/06/07 land, create tiny placeholder files:
       - `frontend/src/pages/Login.tsx` (Plan 03 replaces): `export default function Login() { return <div>TODO Plan 03</div>; }`
       - `frontend/src/pages/Register.tsx` (Plan 03)
       - `frontend/src/pages/Today.tsx` (Plan 07)
       - `frontend/src/pages/Plans.tsx` (Plan 04)
       - `frontend/src/pages/History.tsx` (Plan 07)
       - `frontend/src/pages/Settings.tsx` (Plan 07)
       - `frontend/src/components/auth/PersistStorageWelcome.tsx` (Plan 03 replaces; placeholder for now to avoid import errors)

       (These placeholders are NOT in `files_modified` because they're transient scaffolding; Plans 03/04/06/07 own them.)

    6. **PWA icon placeholders** — generate 4 placeholder PNGs (solid coral background + white "wb" letters):
       - `frontend/public/icons/icon-192.png` (192x192)
       - `frontend/public/icons/icon-512.png` (512x512)
       - `frontend/public/icons/icon-maskable-512.png` (512x512, maskable)
       - `frontend/public/icons/apple-touch-icon-180.png` (180x180)

       Use ImageMagick or any small Node script. Plan 08 may produce final icons during mockup review.

    7. **`frontend/public/version.json`** — placeholder (Plan 06 build process overwrites):
       ```json
       { "version": "0.1.0", "build_hash": "dev" }
       ```
  </action>
  <verify>
    <automated>cd frontend &amp;&amp; pnpm build &amp;&amp; test -f src/main.tsx &amp;&amp; test -f src/App.tsx &amp;&amp; test -f src/router.tsx &amp;&amp; test -f public/icons/icon-192.png &amp;&amp; test -f public/icons/icon-512.png &amp;&amp; test -f public/icons/icon-maskable-512.png &amp;&amp; test -f public/icons/apple-touch-icon-180.png &amp;&amp; test -f public/version.json &amp;&amp; grep -q "import './styles/theme.css'" src/main.tsx</automated>
  </verify>
  <acceptance_criteria>
    - File `frontend/src/main.tsx` contains literal `import './styles/theme.css'` AND `import 'geist/font/sans'` AND `<RouterProvider router={router} />`
    - File `frontend/src/router.tsx` contains literal `createBrowserRouter` AND `lazy: async () =>`
    - File `frontend/src/App.tsx` contains literal `<Outlet />`
    - File `frontend/src/lib/queryClient.ts` contains literal `staleTime: 30_000`
    - All 4 PWA icon files exist with correct sizes
    - File `frontend/public/version.json` contains `"version"` AND `"build_hash"`
    - Command `cd frontend && pnpm build` exits 0
  </acceptance_criteria>
  <done>App shell skeleton complete (main.tsx + App.tsx + router.tsx + queryClient). 4 PWA icons + version.json placeholder ship. Page modules are placeholders that Plans 03/04/06/07 replace. `pnpm build` produces `dist/` with hashed assets.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Browser -> assets | Hashed asset CacheFirst (Plan 06 wires SW); risk minimal in 05a (build only) |
| Tokens -> components | All shadcn primitives consume `var(--color-*)` only — no hardcoded hex |

## STRIDE Threat Register (Plan 05a scope)

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-XSS-01 (token) | Tampering | Hardcoded hex bypasses dark mode contrast / token system | mitigate | ESLint rule from this plan forbids hex literals (`no-restricted-syntax` regex); shadcn primitives explicitly customized to consume `@theme` tokens after `add`; grep verify in acceptance |
| T-A11Y-01 (preview) | DoS (UX) | Components without min-tap-target | mitigate | Button primitive customized with `min-h-11` (44px); UI-06 enforced. Full a11y CI gate is Plan 05b's responsibility |

</threat_model>

<verification>
End-of-plan checks:

```bash
cd frontend
pnpm install
pnpm typecheck
pnpm build  # produces dist/
pnpm lint --max-warnings=0

# Token coverage check (no hardcoded hex)
grep -RnP '#[0-9a-fA-F]{3,8}' frontend/src --include='*.tsx' --include='*.ts' | grep -vE '(theme\.css|globals\.css|\.test\.|no-restricted-syntax)'
# Should return 0 matches
```
</verification>

<success_criteria>
- All Task 1 + Task 2 acceptance criteria met
- `pnpm build` produces `dist/` with hashed assets
- Zero hardcoded hex in `frontend/src` outside `theme.css`/`globals.css`
- All 17 shadcn primitives present and customized to consume `@theme` tokens
- App shell skeleton boots (main.tsx + App.tsx + router.tsx) with lazy page imports
- 4 PWA icon files + version.json placeholder ship
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/01-05a-SUMMARY.md` capturing:
- Final list of installed deps (pnpm ls top-level)
- Confirmation of 17 shadcn primitives present + customizations applied
- Theme token count (spacing/radius/typography/colors light+dark/motion)
- Build artifacts list (dist/ inventory)
</output>
