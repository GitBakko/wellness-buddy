// frontend/tests/e2e/pwa-install.spec.ts
// FND-05 — manifest shape + Service Worker registration.

import { test, expect } from '@playwright/test';

test('PWA manifest is served with correct shape', async ({ page, request }) => {
  await page.goto('/login');
  const manifestHref = await page
    .locator('link[rel="manifest"]')
    .getAttribute('href');
  expect(manifestHref).toBeTruthy();
  const manifestRes = await request.get(manifestHref!);
  expect(manifestRes.ok()).toBe(true);
  const m = (await manifestRes.json()) as {
    name: string;
    display: string;
    start_url: string;
    lang: string;
    icons: { sizes: string; purpose?: string }[];
  };
  expect(m.name).toBe('Wellness Buddy');
  expect(m.display).toBe('standalone');
  expect(m.start_url).toBe('/today');
  expect(m.lang).toBe('it');
  expect(m.icons.length).toBeGreaterThanOrEqual(3);
  // Verify maskable icon present
  expect(m.icons.some((i) => i.purpose === 'maskable')).toBe(true);

  // theme-color meta light + dark
  const themeColors = await page.locator('meta[name="theme-color"]').all();
  expect(themeColors.length).toBeGreaterThanOrEqual(2);
});

test('Service Worker registers on production build', async ({ page }) => {
  await page.goto('/today');
  await page.waitForFunction(() => 'serviceWorker' in navigator, {
    timeout: 5000,
  });
  // Wait briefly for async SW registration
  const registration = await page.evaluate(async () => {
    // up to ~3s for the SW to register
    for (let i = 0; i < 30; i++) {
      const reg = await navigator.serviceWorker.getRegistration();
      if (reg) return 'registered';
      await new Promise((r) => setTimeout(r, 100));
    }
    return 'none';
  });
  expect(registration).toBe('registered');
});
