// frontend/tests/e2e/a11y.spec.ts
// axe-core CI gate (UI-10, T-A11Y-01 mitigation).
//
// Thresholds (CLAUDE.md UI rule 6, UI-SPEC §9):
//   - Body contrast      ≥ 4.5:1 (WCAG 2 AA)
//   - Large/icon contrast ≥ 3.0:1
//   - All routes scanned with `wcag2aa` ruleset
//   - 0 violations required to pass
//
// Routes covered (per UI-SPEC §9 "Per-screen Phase 1 a11y test list"):
//   /login, /signup, /today, /storico, /piano, /impostazioni
//
// Plan 02-08 closure: extended with /settimana/{seed} + /spesa/{seed} to lock
// Phase 2 a11y on the new differentiator surfaces. Deterministic ISO Monday
// 2026-05-04 keeps the boot path stable across runs.
//
// VoiceOver smoke test (real iOS) — NOT covered here. Documented as manual
// pause-gate item in `.planning/phases/01-foundation/01-VALIDATION.md`.
// VoiceOver tooling (`@guidepup/playwright`) is desktop-only and does not
// reflect real iOS behavior; manual real-device check is the only valid signal.

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const ROUTES = [
  '/login',
  '/signup',
  '/today',
  '/settimana/2026-05-04',
  '/spesa/2026-05-04',
  '/storico',
  '/piano',
  '/impostazioni',
];

for (const route of ROUTES) {
  test(`a11y wcag2aa: ${route}`, async ({ page }) => {
    await page.goto(route);
    await page.waitForLoadState('networkidle');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    // Output violations clearly so CI logs are actionable.
    if (results.violations.length > 0) {
      console.error(`Axe violations on ${route}:`, JSON.stringify(results.violations, null, 2));
    }
    expect(results.violations).toHaveLength(0);
  });
}
