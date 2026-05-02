// frontend/tests/visual/dark.spec.ts
// Dark-mode visual regression baseline (UI-12, CLAUDE.md UI rule 5 dark-mode first-class).
// Runs in the `visual-dark` Playwright project (colorScheme: 'dark').
// Pair with light.spec.ts — both must pass for dark-mode parity gate.
//
// TODO (Plan 01-09 follow-up): the Lifesum Pure theme propagation in Plan 01-09
// changes every screenshot baseline (slate-blue bg + leaf signature variants,
// Plus Jakarta typography, macro ring hero, Phosphor iconography).
// Re-record baselines post-merge:
//   pnpm test:visual --update-snapshots
// then commit the new PNGs under `frontend/tests/visual/__screenshots__/`.

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
