// frontend/src/components/week/WeeklyMacroRing.test.tsx
// Plan 02-02 Task 3 — locks the SVG anatomy (4 tracks + 4 arcs), italian
// formatting, ARIA label with "{done} pasti su {total} completati", and
// 0-target/overflow safety mirroring MacroRing.test.tsx.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { WeeklyMacroRing } from '@/components/week/WeeklyMacroRing';
import { italianNumberInt } from '@/lib/format';

describe('WeeklyMacroRing', () => {
  it('renders 8 SVG circles (4 tracks + 4 progress arcs)', () => {
    const { container } = render(
      <WeeklyMacroRing
        kcalConsumed={4200}
        kcalTarget={14000}
        protein={{ current: 320, target: 1120 }}
        carbs={{ current: 540, target: 1750 }}
        fat={{ current: 140, target: 525 }}
        completedMeals={6}
        totalMeals={28}
      />,
    );
    expect(container.querySelectorAll('svg circle').length).toBe(8);
  });

  it('renders italian-formatted weekly kcal value with tabular-nums', () => {
    render(
      <WeeklyMacroRing
        kcalConsumed={4200}
        kcalTarget={14000}
        protein={{ current: 0, target: 1120 }}
        carbs={{ current: 0, target: 1750 }}
        fat={{ current: 0, target: 525 }}
        completedMeals={0}
        totalMeals={28}
      />,
    );
    const expected = italianNumberInt(4200);
    const el = screen.getByText(expected);
    expect(el).toBeInTheDocument();
    expect(el).toHaveStyle({ fontVariantNumeric: 'tabular-nums' });
  });

  it('exposes role="img" + aria-label including "{done} pasti su {total} completati"', () => {
    render(
      <WeeklyMacroRing
        kcalConsumed={4200}
        kcalTarget={14000}
        protein={{ current: 320, target: 1120 }}
        carbs={{ current: 540, target: 1750 }}
        fat={{ current: 140, target: 525 }}
        completedMeals={6}
        totalMeals={28}
      />,
    );
    const ring = screen.getByRole('img', {
      name: /6 pasti su 28 completati/,
    });
    expect(ring).toBeInTheDocument();
  });

  it('renders subtitle "su {target}" + uppercase suffix "kcal · settimana"', () => {
    render(
      <WeeklyMacroRing
        kcalConsumed={3500}
        kcalTarget={14000}
        protein={{ current: 0, target: 1120 }}
        carbs={{ current: 0, target: 1750 }}
        fat={{ current: 0, target: 525 }}
        completedMeals={0}
        totalMeals={28}
      />,
    );
    const target = italianNumberInt(14000);
    expect(screen.getByText(`su ${target}`)).toBeInTheDocument();
    expect(screen.getByText('kcal · settimana')).toBeInTheDocument();
  });

  it('caps progress arcs at 100% when consumption exceeds target', () => {
    const { container } = render(
      <WeeklyMacroRing
        kcalConsumed={50000}
        kcalTarget={14000}
        protein={{ current: 5000, target: 1120 }}
        carbs={{ current: 5000, target: 1750 }}
        fat={{ current: 5000, target: 525 }}
        completedMeals={28}
        totalMeals={28}
      />,
    );
    const arcs = Array.from(container.querySelectorAll('svg circle')).filter(
      (c) => c.getAttribute('stroke-dasharray'),
    );
    for (const arc of arcs) {
      const dash = arc.getAttribute('stroke-dasharray') ?? '';
      const [filledStr, trackStr] = dash.split(' ');
      const filled = parseFloat(filledStr);
      const track = parseFloat(trackStr);
      expect(filled).toBeLessThanOrEqual(track + 0.01);
    }
  });

  it('handles 0-target safely without rendering NaN', () => {
    const { container } = render(
      <WeeklyMacroRing
        kcalConsumed={5000}
        kcalTarget={0}
        protein={{ current: 50, target: 0 }}
        carbs={{ current: 100, target: 0 }}
        fat={{ current: 20, target: 0 }}
        completedMeals={0}
        totalMeals={0}
      />,
    );
    expect(container.textContent).not.toMatch(/NaN/i);
    expect(container.querySelectorAll('svg circle').length).toBe(8);
  });
});
