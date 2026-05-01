// frontend/src/components/__tests__/WeightChart.test.tsx
// UI-08 + PITFALLS#8 — Recharts dark-mode bug requires CSS variable colors.
//
// Two-pronged assertion:
//   1. Source-level: the WeightChart module references CSS variables for stroke +
//      grid colors and contains zero hardcoded hex (Pitfall #8 root cause). The
//      ESLint hex-ban rule covers this at lint time, but we double-check at the
//      module level so accidentally importing a hex constant is caught.
//   2. Render-level: the component mounts without throwing and exposes the
//      Italian aria-label + role=img. (We can't reliably inspect the SVG output
//      of ResponsiveContainer in jsdom because it collapses to 0×0 — that's
//      Recharts' documented behavior in headless DOM.)

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

import { describe, expect, it } from 'vitest';
import { render } from '@testing-library/react';

import { WeightChart } from '@/components/weight/WeightChart';

describe('WeightChart (UI-08, PITFALLS#8 dark-mode)', () => {
  it('source uses CSS variables, not hardcoded hex', () => {
    // Vitest runs from frontend/ — resolve relative to repo source
    const path = resolve(
      __dirname,
      '..',
      'weight',
      'WeightChart.tsx',
    );
    const source = readFileSync(path, 'utf8');
    // PITFALLS#8: stroke + grid colors must reference @theme tokens
    expect(source).toMatch(/var\(--color-neutral-700\)/);
    expect(source).toMatch(/var\(--color-neutral-200\)/);
    // Zero hex literals in the chart source (independent of ESLint).
    // Filter inline data fixtures and comments — direct match for `'#xxxxxx'` in JSX.
    const matches = source.match(/['"#]#[0-9a-fA-F]{3,8}\b/g);
    expect(matches, `Hex literal found in WeightChart source: ${matches}`).toBeNull();
  });

  it('mounts with role=img + Italian aria-label', () => {
    const data = [
      { date: '2026-04-01', weight_kg: 80.0 },
      { date: '2026-04-08', weight_kg: 79.5 },
      { date: '2026-04-15', weight_kg: 79.1 },
    ];
    const { container } = render(<WeightChart data={data} />);
    const region = container.querySelector('[role="img"]');
    expect(region).not.toBeNull();
    expect(region?.getAttribute('aria-label')).toMatch(/peso/i);
  });
});
