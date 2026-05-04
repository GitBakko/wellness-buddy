// frontend/tests/e2e/plan-02-04-screenshots.spec.ts
// Plan 02-04 gap-closure visual capture — non-blocking screenshots saved to
// `playwright-report/plan-02-04/*.png` so the user can verify Bug B/C UI
// shipping quality after E2E goes green.
//
// These tests don't fail; they always save the screenshot. The actual
// behavioral assertions live in `plan-02-04.spec.ts`.

import { test, expect, type Page } from '@playwright/test';

const TODAY_FIXTURE = {
  date: '2026-05-04',
  day_of_week: 0,
  greeting_period: 'morning' as const,
  meals: [
    {
      meal_type: 'breakfast',
      variant_key: 'default',
      title: 'Colazione',
      macros: { kcal: 500, protein_g: 43, carbs_g: 57, fat_g: 18 },
      completed: false,
      photo_url: null,
      ingredients: [
        { name: 'Latte avena/mandorla caldo' },
        { name: "Whey protein" },
        { name: "Fiocchi d'avena integrali" },
      ],
    },
    {
      meal_type: 'lunch',
      variant_key: 'opzione_a',
      title: '3 uova strapazzate + 80 g riso basmati + insalata',
      macros: { kcal: 700, protein_g: 56, carbs_g: 70, fat_g: 21 },
      completed: false,
      photo_url: null,
      ingredients: [
        { name: '3 uova strapazzate' },
        { name: '80 g riso basmati' },
        { name: 'insalata' },
      ],
    },
    {
      meal_type: 'snack',
      variant_key: 'pomeriggio',
      title: 'Spuntino pomeriggio',
      macros: { kcal: 200, protein_g: 16, carbs_g: 20, fat_g: 6 },
      completed: false,
      photo_url: null,
      ingredients: [
        { name: '200 g yogurt di soia' },
        { name: '10 g noci' },
      ],
    },
    {
      meal_type: 'dinner',
      variant_key: 'piatto',
      title: '200 g salmone + 200 g patate + verdura saltata',
      macros: { kcal: 600, protein_g: 48, carbs_g: 60, fat_g: 18 },
      completed: false,
      photo_url: null,
      ingredients: [
        { name: '200 g salmone' },
        { name: '200 g patate' },
        { name: 'verdura saltata' },
      ],
    },
  ],
  weight_today: null,
  workout_today: null,
  macro_target: { kcal: 2000, protein_g: 160, carbs_g: 200, fat_g: 60 },
};

const ME_FIXTURE = {
  id: 'test-user',
  email: 'dev@example.com',
  username: 'dev',
  role: 'admin',
  group_id: null,
  timezone: 'Europe/Rome',
};

function buildWeekly() {
  const dayMeals = (i: number) => [
    {
      slot: 'breakfast',
      title: 'Colazione',
      variant_key: 'default',
      visibility: 'private',
      version: 0,
      updated_at: null,
      completed: false,
      owner_user_id: 'test-user',
      macros: { kcal: 500, protein_g: 43, carbs_g: 57, fat_g: 18 },
      ingredients: [{ name: 'Latte + whey + avena' }],
      options: [],
    },
    {
      slot: 'lunch',
      title: `Pranzo giorno ${i + 1}`,
      variant_key: 'opzione_a',
      visibility: 'group_shared',
      version: 0,
      updated_at: null,
      completed: false,
      owner_user_id: 'test-user',
      macros: { kcal: 700, protein_g: 56, carbs_g: 70, fat_g: 21 },
      ingredients: [
        { name: '3 uova' },
        { name: '80 g riso' },
        { name: 'insalata' },
      ],
      options: [
        { key: 'opzione_a', title: 'Opzione A', macros: { kcal: 700 } },
        { key: 'opzione_b', title: 'Opzione B', macros: { kcal: 700 } },
      ],
    },
    {
      slot: 'dinner',
      title: `Cena giorno ${i + 1}`,
      variant_key: 'piatto',
      visibility: 'group_shared',
      version: 0,
      updated_at: null,
      completed: false,
      owner_user_id: 'test-user',
      macros: { kcal: 600, protein_g: 48, carbs_g: 60, fat_g: 18 },
      ingredients: [
        { name: '200 g salmone' },
        { name: '200 g patate' },
        { name: 'verdura saltata' },
      ],
      options: [{ key: 'piatto', title: 'Piatto', macros: { kcal: 600 } }],
    },
    {
      slot: 'snack',
      title: 'Spuntino',
      variant_key: 'pomeriggio',
      visibility: 'private',
      version: 0,
      updated_at: null,
      completed: false,
      owner_user_id: 'test-user',
      macros: { kcal: 200, protein_g: 16, carbs_g: 20, fat_g: 6 },
      ingredients: [{ name: 'yogurt + noci' }],
      options: [],
    },
  ];
  const days = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(2026, 4, 4 + i);
    return {
      date: date.toISOString().slice(0, 10),
      day_of_week: i,
      meals: dayMeals(i),
    };
  });
  return {
    week_start: '2026-05-04',
    days,
    totals: { kcal: 14000, protein_g: 1120, carbs_g: 1400, fat_g: 420 },
  };
}

async function bootstrap(page: Page) {
  await page.route('**/api/auth/me', (r) =>
    r.fulfill({ status: 200, body: JSON.stringify(ME_FIXTURE) }),
  );
  await page.route('**/api/auth/refresh', (r) =>
    r.fulfill({ status: 200, body: JSON.stringify({ access_token: 'fake' }) }),
  );
  await page.route('**/api/today', (r) =>
    r.fulfill({ status: 200, body: JSON.stringify(TODAY_FIXTURE) }),
  );
  await page.route('**/api/weekly/2026-05-04', (r) =>
    r.fulfill({ status: 200, body: JSON.stringify(buildWeekly()) }),
  );
  await page.route('**/api/plans', (r) =>
    r.fulfill({ status: 200, body: '[]' }),
  );
  await page.route('**/api/errors', (r) => r.fulfill({ status: 204 }));
  await page.route('**/version.json', (r) =>
    r.fulfill({
      status: 200,
      body: JSON.stringify({ version: '0.2.0', build_hash: 'dev' }),
    }),
  );
}

test.describe('Plan 02-04 visual proof', () => {
  test('today screenshot — MealCards with ingredients + MacroRing', async ({
    page,
  }) => {
    await bootstrap(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('article').first()).toBeVisible();
    await page.screenshot({
      path: 'playwright-report/plan-02-04/today.png',
      fullPage: true,
    });
  });

  test('settimana screenshot — week picker + day rows with composition', async ({
    page,
  }) => {
    await bootstrap(page);
    await page.goto('/settimana/2026-05-04');
    await page.waitForLoadState('networkidle');
    await expect(
      page.locator('div[role="group"][aria-label="Settimana corrente"]'),
    ).toBeVisible();
    await page.screenshot({
      path: 'playwright-report/plan-02-04/settimana.png',
      fullPage: true,
    });
  });
});
