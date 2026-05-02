// frontend/src/components/week/DayCompletionStrip.test.tsx
// Plan 02-02 Task 3 — locks the 7-day rendering, state classification, italian
// day labels, and aria labels for each pill state.

import { describe, expect, it } from 'vitest';
import { render } from '@testing-library/react';

import { DayCompletionStrip } from '@/components/week/DayCompletionStrip';

describe('DayCompletionStrip', () => {
  it('renders exactly 7 day cells', () => {
    const days = Array.from({ length: 7 }, (_, i) => ({
      dayOfWeek: i,
      completedCount: 0,
      totalCount: 4,
    }));
    const { container } = render(<DayCompletionStrip days={days} />);
    const cells = container.querySelectorAll('[data-state]');
    expect(cells.length).toBe(7);
  });

  it('classifies "done" when completed===total>0', () => {
    const days = [
      { dayOfWeek: 0, completedCount: 4, totalCount: 4 },
      { dayOfWeek: 1, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 2, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 3, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 4, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 5, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 6, completedCount: 0, totalCount: 4 },
    ];
    const { container } = render(<DayCompletionStrip days={days} />);
    const cells = container.querySelectorAll('[data-state]');
    expect(cells[0].getAttribute('data-state')).toBe('done');
  });

  it('classifies "partial" when 0 < completed < total', () => {
    const days = [
      { dayOfWeek: 0, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 1, completedCount: 2, totalCount: 4 },
      { dayOfWeek: 2, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 3, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 4, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 5, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 6, completedCount: 0, totalCount: 4 },
    ];
    const { container } = render(<DayCompletionStrip days={days} />);
    const cells = container.querySelectorAll('[data-state]');
    expect(cells[1].getAttribute('data-state')).toBe('partial');
  });

  it('classifies "blank" when totalCount===0', () => {
    const days = [
      { dayOfWeek: 0, completedCount: 0, totalCount: 0 },
      { dayOfWeek: 1, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 2, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 3, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 4, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 5, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 6, completedCount: 0, totalCount: 4 },
    ];
    const { container } = render(<DayCompletionStrip days={days} />);
    const cells = container.querySelectorAll('[data-state]');
    expect(cells[0].getAttribute('data-state')).toBe('blank');
  });

  it('emits italian aria-label for each day per state', () => {
    const days = [
      { dayOfWeek: 0, completedCount: 4, totalCount: 4 },
      { dayOfWeek: 1, completedCount: 2, totalCount: 4 },
      { dayOfWeek: 2, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 3, completedCount: 0, totalCount: 0 },
      { dayOfWeek: 4, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 5, completedCount: 0, totalCount: 4 },
      { dayOfWeek: 6, completedCount: 0, totalCount: 4 },
    ];
    const { container } = render(<DayCompletionStrip days={days} />);
    const cells = container.querySelectorAll('[data-state]');
    expect(cells[0].getAttribute('aria-label')).toContain('Lunedì');
    expect(cells[0].getAttribute('aria-label')).toContain(
      'Tutti i pasti completati',
    );
    expect(cells[1].getAttribute('aria-label')).toContain(
      '2 di 4 pasti completati',
    );
    expect(cells[2].getAttribute('aria-label')).toContain('Pianificato');
    expect(cells[3].getAttribute('aria-label')).toContain('Nessun piano');
  });

  it('renders 3-letter italian day captions (Lun · Mar · Mer · Gio · Ven · Sab · Dom)', () => {
    const days = Array.from({ length: 7 }, (_, i) => ({
      dayOfWeek: i,
      completedCount: 0,
      totalCount: 4,
    }));
    const { container } = render(<DayCompletionStrip days={days} />);
    expect(container.textContent).toContain('Lun');
    expect(container.textContent).toContain('Mar');
    expect(container.textContent).toContain('Mer');
    expect(container.textContent).toContain('Gio');
    expect(container.textContent).toContain('Ven');
    expect(container.textContent).toContain('Sab');
    expect(container.textContent).toContain('Dom');
  });
});
