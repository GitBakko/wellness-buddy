// frontend/playwright.dev.config.ts
// Plan 02-04 gap-closure E2E config — runs against `pnpm dev` (port 5173) so
// /api/* requests proxy to FastAPI on :8001. Used to validate Bug A (parser
// allowlist), Bug B (/today ingredients + macros + non-100% ring), Bug C
// (/settimana composition + macros + week picker UX) end-to-end.
//
// Difference vs playwright.config.ts:
//   - baseURL points at the dev server (HMR), NOT the preview build
//   - webServer is OFF (we assume `pnpm dev` is already running, started by
//     the calling agent / human — avoids Vite "port in use" race)
//   - Single iPhone-13 project to keep CI light; UI-13 mobile-first remains
//     the primary surface validated.

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  // Plan 02-04 gap-closure tests + Plan 02-08 family-convergence (FAM-09).
  // Both run against `pnpm dev` because they stub `/api/*` at the page-route
  // layer and need React's full HMR module graph (no preview build needed).
  testMatch: /e2e\/(plan-02-04(-screenshots)?|family-convergence)\.spec\.ts/,
  fullyParallel: false, // sequential so the same auth state is reused
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: 'list',

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    contextOptions: { reducedMotion: 'reduce' },
  },

  // No webServer — assume `pnpm dev` is already running.

  projects: [
    {
      name: 'iphone-13',
      use: { ...devices['iPhone 13'] },
    },
  ],

  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01 },
  },
});
