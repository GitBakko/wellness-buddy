// frontend/src/components/today/MacroRing.test.tsx
// Plan 01-09 Task 2 — locks the SVG structure, tabular-nums kcal value,
// progress arc rendering, accessibility label, and overflow/zero edge cases.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { MacroRing } from '@/components/today/MacroRing';
import { italianNumberInt } from '@/lib/format';

describe('MacroRing', () => {
  it('renders 8 SVG circles (4 tracks + 4 progress arcs)', () => {
    const { container } = render(
      <MacroRing
        kcalConsumed={1760}
        kcalTarget={2200}
        protein={{ current: 78, target: 120 }}
        carbs={{ current: 165, target: 250 }}
        fat={{ current: 52, target: 75 }}
      />,
    );
    const circles = container.querySelectorAll('svg circle');
    expect(circles.length).toBe(8);
  });

  it('renders kcal value with italian thousands formatting + tabular-nums', () => {
    render(
      <MacroRing
        kcalConsumed={1760}
        kcalTarget={2200}
        protein={{ current: 0, target: 120 }}
        carbs={{ current: 0, target: 250 }}
        fat={{ current: 0, target: 75 }}
      />,
    );
    // Use the runtime italian formatter so this test passes whether or not the
    // host has full-icu installed (Node-default jsdom may fall back to en-US output).
    const expected = italianNumberInt(1760);
    const kcalEl = screen.getByText(expected);
    expect(kcalEl).toBeInTheDocument();
    // Tabular-nums declared via inline style for SVG-adjacent layout
    expect(kcalEl).toHaveStyle({ fontVariantNumeric: 'tabular-nums' });
  });

  it('emits stroke-dasharray with 0 filled portion when consumption is 0', () => {
    const { container } = render(
      <MacroRing
        kcalConsumed={0}
        kcalTarget={2200}
        protein={{ current: 0, target: 120 }}
        carbs={{ current: 0, target: 250 }}
        fat={{ current: 0, target: 75 }}
      />,
    );
    // The 4 progress arcs have stroke-dasharray; the 4 tracks do not.
    const arcs = Array.from(container.querySelectorAll('svg circle')).filter(
      (c) => c.getAttribute('stroke-dasharray'),
    );
    expect(arcs.length).toBe(4);
    for (const arc of arcs) {
      const dash = arc.getAttribute('stroke-dasharray') ?? '';
      expect(dash.startsWith('0.00 ')).toBe(true);
    }
  });

  it('caps progress arc at 100% when consumption exceeds target (no negative offset)', () => {
    const { container } = render(
      <MacroRing
        kcalConsumed={5000}
        kcalTarget={2200}
        protein={{ current: 200, target: 120 }}
        carbs={{ current: 500, target: 250 }}
        fat={{ current: 200, target: 75 }}
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
      // Filled segment never exceeds the full circumference (within 0.01 tolerance).
      expect(filled).toBeLessThanOrEqual(track + 0.01);
    }
  });

  it('exposes role="img" + aria-label following "{consumed} di {target} kcal oggi" pattern', () => {
    render(
      <MacroRing
        kcalConsumed={1760}
        kcalTarget={2200}
        protein={{ current: 78, target: 120 }}
        carbs={{ current: 165, target: 250 }}
        fat={{ current: 52, target: 75 }}
      />,
    );
    const consumed = italianNumberInt(1760);
    const target = italianNumberInt(2200);
    const ring = screen.getByRole('img', {
      name: `${consumed} di ${target} kcal oggi`,
    });
    expect(ring).toBeInTheDocument();
  });

  it('renders subtitle "su {target}" + uppercase suffix "kcal oggi"', () => {
    render(
      <MacroRing
        kcalConsumed={1200}
        kcalTarget={2000}
        protein={{ current: 0, target: 120 }}
        carbs={{ current: 0, target: 250 }}
        fat={{ current: 0, target: 75 }}
      />,
    );
    const target = italianNumberInt(2000);
    expect(screen.getByText(`su ${target}`)).toBeInTheDocument();
    expect(screen.getByText('kcal oggi')).toBeInTheDocument();
  });

  it('handles 0-target safely without rendering NaN', () => {
    const { container } = render(
      <MacroRing
        kcalConsumed={500}
        kcalTarget={0}
        protein={{ current: 50, target: 0 }}
        carbs={{ current: 100, target: 0 }}
        fat={{ current: 20, target: 0 }}
      />,
    );
    // No "NaN" anywhere in the rendered DOM
    expect(container.textContent).not.toMatch(/NaN/i);
    // Circles still render
    expect(container.querySelectorAll('svg circle').length).toBe(8);
  });
});
