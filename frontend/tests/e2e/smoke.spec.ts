// frontend/tests/e2e/smoke.spec.ts
// Phase 1 smoke test — app boots and renders the root without runtime errors.
// Runs against the built `pnpm preview` bundle (Pitfall #12).

import { test, expect } from '@playwright/test';

test('app boots and renders root html', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (err) => errors.push(err.message));
  page.on('console', (msg) => {
    if (msg.type() !== 'error') return;
    const text = msg.text();
    // AppShell legitimately polls /api/auth/me + /api/plans + /api/errors via
    // useDexieResync/ErrorBoundary. Those endpoints are NetworkOnly per
    // vite.config.ts and 404 against the unmocked preview server. Filter
    // network-resource 404s; keep real JS runtime errors.
    if (
      text.includes('Failed to load resource') ||
      text.includes('/api/') ||
      text.includes('the server responded with a status of 404')
    ) {
      return;
    }
    errors.push(text);
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  // Root HTML element must render with the app document title.
  await expect(page).toHaveTitle(/Wellness Buddy/i);

  // Some content must paint inside #root (router redirects / to /today, which renders
  // a placeholder until Plan 07 lands — anything inside #root counts as "boots").
  const root = page.locator('#root');
  await expect(root).not.toBeEmpty();

  // Zero JS runtime errors (network-resource 404s filtered above — those are
  // expected when preview runs without a backend).
  expect(errors, `Page emitted runtime errors: ${errors.join('\n')}`).toHaveLength(0);
});

test('app exposes Italian lang attribute on <html>', async ({ page }) => {
  await page.goto('/');
  const lang = await page.locator('html').getAttribute('lang');
  expect(lang).toBe('it');
});
