// frontend/tests/visual/light.spec.ts
// Light-mode visual regression baseline (UI-12 dark-mode + token system enforcement).
// Runs in the `visual-light` Playwright project (colorScheme: 'light').
// Pair with dark.spec.ts — both must pass for dark-mode parity gate.
//
// Plan 02-02 (D-31): baselines regenerated post Lifesum Pure (Plan 01-09)
// + new /settimana route. Use the deterministic seed Monday 2026-05-04 for
// the /settimana fixture so screenshots are stable across runs.
//
// To re-record after a deliberate UI change: `pnpm test:visual --update-snapshots`
// then commit the new PNGs under `frontend/tests/visual/__screenshots__/`.

import { test, expect } from '@playwright/test';

const ROUTES = [
  '/login',
  '/today',
  '/settimana/2026-05-04',
  '/piano',
  '/impostazioni',
];

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
