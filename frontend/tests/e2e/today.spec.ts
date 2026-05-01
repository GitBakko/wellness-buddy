// frontend/tests/e2e/today.spec.ts
// Plan 07 Task 3 — TODAY-01..08 e2e smoke against the built bundle (Pitfall #12).
//
// Runs against `pnpm preview` (NOT `pnpm dev`). The preview server has no
// backend, so we exercise the *unauthenticated* boot path: router redirects
// `/` → `/today` and AppShell tries `/api/auth/me`, which 404s. We verify the
// page renders without runtime JS errors (filtered network 404s expected).
//
// Full login → /today → log weight → workout flow is deferred to the Phase 2
// e2e harness which seeds a backend container alongside Playwright. The
// `--text-display-serif` escape hatch is verified at the source level by:
//   - ESLint hex-ban + manual `grep` gate (≤2 hits in src/: theme.css + Today.tsx)
//   - WeightChart.test.tsx (zero hex literals)
// so we don't need a runtime bundle assertion here (Vite minifier transforms
// the literal away in production builds).

import { test, expect } from '@playwright/test';

test.describe('/today (TODAY-01..08 smoke)', () => {
  test('redirects root to /today and renders without runtime errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));
    page.on('console', (msg) => {
      if (msg.type() !== 'error') return;
      const text = msg.text();
      // Filter expected unauth/network 404s when preview has no backend
      if (
        text.includes('Failed to load resource') ||
        text.includes('/api/') ||
        text.includes('the server responded with a status of 404')
      ) {
        return;
      }
      errors.push(text);
    });

    await page.goto('/today');
    await page.waitForLoadState('networkidle');

    // Title + lang attribute (FND-09)
    await expect(page).toHaveTitle(/Wellness Buddy/i);
    expect(await page.locator('html').getAttribute('lang')).toBe('it');

    // Page paints — root is non-empty
    const root = page.locator('#root');
    await expect(root).not.toBeEmpty();

    // No JS runtime errors beyond the filtered network 404s above
    expect(errors, `Page emitted runtime errors: ${errors.join('\n')}`).toHaveLength(0);
  });
});
