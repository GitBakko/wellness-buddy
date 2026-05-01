// frontend/tests/visual/light.spec.ts
// Light-mode visual regression baseline (UI-12 dark-mode + token system enforcement).
// Runs in the `visual-light` Playwright project (colorScheme: 'light').
// Pair with dark.spec.ts — both must pass for dark-mode parity gate.

import { test, expect } from '@playwright/test';

const ROUTES = ['/login', '/today', '/piano', '/impostazioni'];

for (const route of ROUTES) {
  test(`visual-light: ${route}`, async ({ page }) => {
    await page.goto(route);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot(`light${route.replace(/\//g, '_') || '_root'}.png`, {
      maxDiffPixelRatio: 0.02,
      animations: 'disabled',
      fullPage: false,
    });
  });
}
