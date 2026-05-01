// frontend/tests/visual/dark.spec.ts
// Dark-mode visual regression baseline (UI-12, CLAUDE.md UI rule 5 dark-mode first-class).
// Runs in the `visual-dark` Playwright project (colorScheme: 'dark').
// Pair with light.spec.ts — both must pass for dark-mode parity gate.

import { test, expect } from '@playwright/test';

const ROUTES = ['/login', '/today', '/piano', '/impostazioni'];

for (const route of ROUTES) {
  test(`visual-dark: ${route}`, async ({ page }) => {
    await page.goto(route);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot(`dark${route.replace(/\//g, '_') || '_root'}.png`, {
      maxDiffPixelRatio: 0.02,
      animations: 'disabled',
      fullPage: false,
    });
  });
}
