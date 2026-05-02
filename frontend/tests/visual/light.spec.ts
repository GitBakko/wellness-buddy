// frontend/tests/visual/light.spec.ts
// Light-mode visual regression baseline (UI-12 dark-mode + token system enforcement).
// Runs in the `visual-light` Playwright project (colorScheme: 'light').
// Pair with dark.spec.ts — both must pass for dark-mode parity gate.
//
// TODO (Plan 01-09 follow-up): the Lifesum Pure theme propagation in Plan 01-09
// changes every screenshot baseline (warmer cream bg, sage-leaf primary,
// Plus Jakarta typography, macro ring hero, Phosphor iconography).
// Re-record baselines post-merge:
//   pnpm test:visual --update-snapshots
// then commit the new PNGs under `frontend/tests/visual/__screenshots__/`.

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
