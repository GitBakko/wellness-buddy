// frontend/tests/e2e/smoke.spec.ts
// Phase 1 smoke test — app boots and renders the root without runtime errors.
// Runs against the built `pnpm preview` bundle (Pitfall #12).

import { test, expect } from '@playwright/test';

test('app boots and renders root html', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (err) => errors.push(err.message));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  // Root HTML element must render with the app document title.
  await expect(page).toHaveTitle(/Wellness Buddy/i);

  // Some content must paint inside #root (router redirects / to /today, which renders
  // a placeholder until Plan 07 lands — anything inside #root counts as "boots").
  const root = page.locator('#root');
  await expect(root).not.toBeEmpty();

  // Zero runtime errors.
  expect(errors, `Page emitted runtime errors: ${errors.join('\n')}`).toHaveLength(0);
});

test('app exposes Italian lang attribute on <html>', async ({ page }) => {
  await page.goto('/');
  const lang = await page.locator('html').getAttribute('lang');
  expect(lang).toBe('it');
});
