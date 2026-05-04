// frontend/src/services/__tests__/shopping.test.ts
// Plan 02-05 — locks the composeTextExport contract used by the "Copia testo"
// CTA. Output format must match the WeasyPrint PDF template (Plan 02-06)
// so users can paste the list into messages / notes.

import { describe, expect, it } from 'vitest';

import { composeTextExport } from '@/services/shopping';
import type { ShoppingResponse } from '@/services/shopping';

const fixture: ShoppingResponse = {
  week_start: '2026-05-04',
  version: 0,
  categories: [
    {
      name: 'Frigo & Freschi',
      items: [
        {
          canonical_name: 'yogurt greco',
          name_display: 'Yogurt Greco',
          amount: 200,
          unit: 'g',
          quantity_it: '200 g',
          category: 'Frigo & Freschi',
          checked: false,
          sources: [],
        },
        {
          canonical_name: 'salmone',
          name_display: 'Salmone',
          amount: 200,
          unit: 'g',
          quantity_it: '200 g',
          category: 'Frigo & Freschi',
          checked: true,
          sources: [],
        },
      ],
    },
    {
      name: 'Frutta & Verdura',
      items: [],
    },
    {
      name: 'Dispensa',
      items: [
        {
          canonical_name: 'pasta',
          name_display: 'Pasta',
          amount: 80,
          unit: 'g',
          quantity_it: '80 g',
          category: 'Dispensa',
          checked: false,
          sources: [],
        },
      ],
    },
    { name: 'Condimenti', items: [] },
    { name: 'Integratori', items: [] },
  ],
};

describe('composeTextExport', () => {
  it('renders header, skips empty categories, marks checked items with [x]', () => {
    const out = composeTextExport(fixture);
    // Header
    expect(out).toMatch(/^Lista spesa — settimana del 2026-05-04/);
    // Filled categories present
    expect(out).toContain('## Frigo & Freschi');
    expect(out).toContain('## Dispensa');
    // Empty categories skipped
    expect(out).not.toContain('## Frutta & Verdura');
    expect(out).not.toContain('## Condimenti');
    // Checked vs unchecked markers
    expect(out).toContain('[x] Salmone — 200 g');
    expect(out).toContain('[ ] Yogurt Greco — 200 g');
    expect(out).toContain('[ ] Pasta — 80 g');
  });

  it('omits trailing whitespace', () => {
    const out = composeTextExport(fixture);
    expect(out.endsWith(' ')).toBe(false);
    expect(out.endsWith('\n')).toBe(false);
  });
});
