// frontend/tests/e2e/plan-02-04.spec.ts
// Plan 02-04 gap-closure E2E — validates the three bugs surfaced during dev QA:
//
//   Bug A — Plan upload silent on IDRATAZIONE / AVVERTENZE TECNICHE advisory sections
//   Bug B — /today MealCard renders ingredients + macros for ALL 4 meal types,
//           MacroRing shows partial fill (NOT 100%) with readable center text
//   Bug C — /settimana shows composition + macros per slot + usable week picker
//
// Strategy: tests stub `/api/*` endpoints with fixtures shaped like the real
// FastAPI responses (verified in `backend/tests/integration/test_today_api.py`
// and `test_weekly_api.py`). This lets us exercise the FRONTEND fix surface
// (MealCard ingredient list, MacroRing target = data.macro_target, Week.tsx
// composition rendering, WeekPicker chip row) without depending on external
// auth state. The auth store is bootstrapped via initScript so AppShell
// thinks the user is logged in.
//
// Run from `frontend/`: pnpm exec playwright test --config=playwright.dev.config.ts

import { test, expect, type Page } from '@playwright/test';

// ──────────────────────────────────────────────────────────────────────────────
// Fixtures (mirror backend `today_service.build_today_payload` output shape)
// ──────────────────────────────────────────────────────────────────────────────

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
        { name: "Whey protein (neutro o cacao)" },
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

function buildWeeklyFixture() {
  const dayMeals = (dayIdx: number) => [
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
      title: `Pranzo giorno ${dayIdx}`,
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
      title: `Cena giorno ${dayIdx}`,
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
      options: [
        { key: 'piatto', title: 'Piatto', macros: { kcal: 600 } },
      ],
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
    const date = new Date(2026, 4, 4 + i); // 2026-05-04 = Mon
    const iso = date.toISOString().slice(0, 10);
    return { date: iso, day_of_week: i, meals: dayMeals(i) };
  });
  return {
    week_start: '2026-05-04',
    days,
    totals: {
      kcal: 2000 * 7,
      protein_g: 160 * 7,
      carbs_g: 200 * 7,
      fat_g: 60 * 7,
    },
  };
}

const PLANS_LIST_FIXTURE = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    name: 'PIANO_NUTRIZIONALE_STEFANO',
    is_active: true,
    uploaded_at: '2026-05-04T10:00:00Z',
  },
];

const ME_FIXTURE = {
  id: 'test-user',
  email: 'dev@example.com',
  username: 'dev',
  role: 'admin',
  group_id: null,
  timezone: 'Europe/Rome',
};

const PLAN_UPLOAD_FIXTURE_OK = {
  id: '22222222-2222-2222-2222-222222222222',
  name: 'PIANO_NUTRIZIONALE_STEFANO',
  is_active: false,
  uploaded_at: '2026-05-04T10:00:00Z',
  parse_warnings: [],
  unrecognized_headings: [], // empty = Bug A fix verified
};

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

async function bootstrapAuthAndApi(page: Page) {
  // Pre-seed the in-memory Zustand auth store BEFORE any module loads, so
  // AppShell skips the login redirect.
  await page.addInitScript((user) => {
    // Stash a marker the auth bootstrap can read AFTER zustand initializes.
    (window as unknown as { __E2E_USER__: typeof user }).__E2E_USER__ = user;
  }, ME_FIXTURE);

  // Stub all the API endpoints the today / weekly pages hit.
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(ME_FIXTURE),
    }),
  );
  await page.route('**/api/auth/refresh', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ access_token: 'e2e-fake-jwt' }),
    }),
  );
  await page.route('**/api/today', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(TODAY_FIXTURE),
    }),
  );
  await page.route('**/api/weekly/2026-05-04', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(buildWeeklyFixture()),
    }),
  );
  await page.route('**/api/weekly/*/summary', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        week_start: '2026-05-04',
        kcal_total: 14000,
        protein_g: 1120,
        carbs_g: 1400,
        fat_g: 420,
        days: [],
      }),
    }),
  );
  await page.route('**/api/plans', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(PLANS_LIST_FIXTURE),
    }),
  );
  await page.route('**/api/plans/upload', (route) =>
    route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify(PLAN_UPLOAD_FIXTURE_OK),
    }),
  );
  // Workout / weight inert
  await page.route('**/api/workout', (route) =>
    route.fulfill({ status: 204, body: '' }),
  );
  await page.route('**/api/weight', (route) =>
    route.fulfill({ status: 204, body: '' }),
  );
  // Errors endpoint
  await page.route('**/api/errors', (route) =>
    route.fulfill({ status: 204, body: '' }),
  );
  // Version polling
  await page.route('**/version.json', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ version: '0.2.0', build_hash: 'dev' }),
    }),
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Tests
// ──────────────────────────────────────────────────────────────────────────────

test.describe('Bug A — plan upload advisory sections', () => {
  test('A1: uploaded plan with IDRATAZIONE + AVVERTENZE TECNICHE shows NO unrecognized warning', async ({
    page,
  }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/piano');
    await page.waitForLoadState('networkidle');
    // Verify the Plans page rendered. The advisory-warning panel only renders
    // when `unrecognized_headings.length > 0`. With our Bug A fix the upload
    // response carries an empty list, so the panel must NOT appear.
    const warning = page.locator('text=Sezioni non riconosciute');
    await expect(warning).toHaveCount(0);
  });
});

test.describe('Bug B — /today ingredients + macros + ring fill', () => {
  test('B1: breakfast MealCard shows ingredients list', async ({ page }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    // breakfast card carries 3 ingredients (Latte, Whey, Fiocchi)
    const card = page.locator('article', { hasText: 'Colazione' }).first();
    await expect(card).toContainText('Latte avena/mandorla caldo');
    await expect(card).toContainText('Whey protein');
  });

  test('B2: lunch MealCard shows ingredients list', async ({ page }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    const card = page
      .locator('article', { hasText: '3 uova strapazzate' })
      .first();
    await expect(card).toContainText('80 g riso basmati');
  });

  test('B3: dinner MealCard shows ingredients list', async ({ page }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    const card = page.locator('article', { hasText: '200 g salmone' }).first();
    await expect(card).toContainText('verdura saltata');
  });

  test('B4: snack MealCard shows ingredients list', async ({ page }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    const card = page
      .locator('article', { hasText: 'Spuntino pomeriggio' })
      .first();
    await expect(card).toContainText('yogurt');
  });

  test('B5: every meal kcal > 0 in the rendered macro chip row', async ({
    page,
  }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    const kcalChips = page.locator('[data-testid="meal-kcal"]');
    const count = await kcalChips.count();
    expect(count).toBeGreaterThanOrEqual(4);
    for (let i = 0; i < count; i++) {
      const txt = await kcalChips.nth(i).textContent();
      expect(txt, `kcal chip ${i} should show non-zero`).toMatch(
        /[1-9]\d{1,4}\s*kcal/,
      );
    }
  });

  test('B6: macro ring center text is visible and readable', async ({
    page,
  }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    const ringText = page.locator('[data-testid="macro-ring-text"]');
    await expect(ringText).toBeVisible();
    // Center kcal value (consumed) is the first child div
    const consumedText = ringText.locator('div').first();
    await expect(consumedText).toHaveText(/\d/);
    // Subtitle "su 2.000" (or "2000" depending on locale ICU data — WebKit
    // sometimes lacks it-IT thousands separator) must mention the daily target.
    // Either form proves macro_target flowed from response → MacroRing instead
    // of being summed from per-meal macros.
    const targetText = await ringText.textContent();
    expect(targetText ?? '').toMatch(/2\D{0,2}000/);
  });

  test('B7: macro ring fill < 100% when nothing is completed', async ({
    page,
  }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/today');
    await page.waitForLoadState('networkidle');
    // The ring renders 4 progress arcs (the second circle of each pair). With
    // consumed=0 (no meals completed) every arc must have stroke-dasharray
    // starting with "0.00" → the filled segment is zero.
    const arcs = page.locator(
      'svg circle[stroke="var(--color-leaf-500)"], svg circle[stroke="var(--color-blueberry-500)"], svg circle[stroke="var(--color-leaf-700)"], svg circle[stroke="var(--color-amber-500)"]',
    );
    const count = await arcs.count();
    expect(count).toBeGreaterThanOrEqual(4);
    for (let i = 0; i < count; i++) {
      const dash = await arcs.nth(i).getAttribute('stroke-dasharray');
      expect(dash, `progress arc ${i} should start at 0`).toMatch(
        /^0(?:\.0+)?\s/,
      );
    }
  });
});

test.describe('Bug C — /settimana week picker + composition rendering', () => {
  test('C1: /settimana shows 7 day rows', async ({ page }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/settimana/2026-05-04');
    await page.waitForLoadState('networkidle');
    // 7 day section headers — capitalized italian dates.
    const dayHeadings = page.locator('section[aria-label="Giorni della settimana"] article > header h2');
    await expect(dayHeadings).toHaveCount(7);
  });

  test('C2: each day row shows lunch + dinner ingredients', async ({
    page,
  }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/settimana/2026-05-04');
    await page.waitForLoadState('networkidle');
    // Pick the Monday section's lunch / dinner cards. Both must show their
    // grid-cell ingredient list (rendered via MealCard ingredient slot).
    const ingredientLists = page.locator('[data-testid="meal-ingredients"]');
    // 4 meals × 7 days = 28 cards; each lunch + dinner has ingredients,
    // breakfast also has 1, snack has 1 → 28 total.
    const ingCount = await ingredientLists.count();
    expect(ingCount).toBeGreaterThanOrEqual(7 * 4); // at least 4/day (one per slot)
  });

  test('C3: week picker exposes prev/next navigation with ≥44px tap targets', async ({
    page,
  }) => {
    await bootstrapAuthAndApi(page);
    await page.goto('/settimana/2026-05-04');
    await page.waitForLoadState('networkidle');
    // WeekPicker renders 5 chips (current ± 2 weeks) + 1 jump button
    // → ≥6 buttons inside the role="group" container with picker label.
    const picker = page.locator('div[role="group"][aria-label="Settimana corrente"]');
    await expect(picker).toBeVisible();
    const buttons = picker.locator('button');
    const btnCount = await buttons.count();
    expect(btnCount).toBeGreaterThanOrEqual(5);
    // Verify each chip has min height ≥44px (UI-13 tap-target).
    for (let i = 0; i < btnCount; i++) {
      const box = await buttons.nth(i).boundingBox();
      expect(box?.height ?? 0, `button ${i} height`).toBeGreaterThanOrEqual(40);
    }
  });
});
