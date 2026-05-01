// frontend/playwright.config.ts
// E2E + a11y + visual diff config (Pitfall #12 — runs against `pnpm preview` of built dist,
// NOT `pnpm dev`, so we exercise the production bundle).
//
// Projects:
//   - axe           → tests/e2e/a11y.spec.ts on Desktop Chrome (UI-10, T-A11Y-01 mitigation)
//   - visual-light  → tests/visual/light.spec.ts (colorScheme: 'light')
//   - visual-dark   → tests/visual/dark.spec.ts (colorScheme: 'dark', UI-12)
//   - iphone-13     → tests/e2e/*.spec.ts on iPhone 13 viewport (UI-13 mobile-first)
//   - chromium      → tests/e2e/*.spec.ts on Desktop Chrome
//
// `contextOptions.reducedMotion: 'reduce'` ensures all e2e + visual diff runs
// happen with prefers-reduced-motion: reduce (UI-05 + T-MOTION-01) — tests
// that animations are zeroed in CI is the gate.

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? [['github'], ['list']] : 'list',

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:4173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    contextOptions: { reducedMotion: 'reduce' },
  },

  webServer: {
    command: 'pnpm preview --port 4173',
    port: 4173,
    timeout: 60_000,
    reuseExistingServer: !process.env.CI,
  },

  projects: [
    {
      name: 'axe',
      testMatch: /a11y\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'visual-light',
      testMatch: /visual\/light\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], colorScheme: 'light' },
    },
    {
      name: 'visual-dark',
      testMatch: /visual\/dark\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], colorScheme: 'dark' },
    },
    {
      name: 'iphone-13',
      testMatch: /e2e\/.*\.spec\.ts/,
      testIgnore: /a11y\.spec\.ts/,
      use: { ...devices['iPhone 13'] },
    },
    {
      name: 'chromium',
      testMatch: /e2e\/.*\.spec\.ts/,
      testIgnore: /a11y\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01 },
  },
});
