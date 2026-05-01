// frontend/tests/e2e/pwa-update.spec.ts
// FND-06 — verify update toast appears when /version.json reports a build_hash
// different from the build the page is running.
//
// Strategy: mock /version.json to return 'changed-hash'. AppShell mounts
// useVersionPolling on load; first poll happens immediately + on
// visibilitychange → toast renders.

import { test, expect } from '@playwright/test';

test('update toast appears when /version.json mismatches build hash', async ({
  page,
}) => {
  await page.route('**/version.json', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ version: '0.1.0', build_hash: 'changed-hash' }),
    });
  });

  await page.goto('/today');
  // Trigger visibilitychange to fast-track polling on top of initial check.
  await page.evaluate(() =>
    document.dispatchEvent(new Event('visibilitychange')),
  );

  await expect(page.getByText('Nuova versione disponibile')).toBeVisible({
    timeout: 10_000,
  });
  await expect(page.getByRole('button', { name: 'Ricarica' })).toBeVisible();
});
