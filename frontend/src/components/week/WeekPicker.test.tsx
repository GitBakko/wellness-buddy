// frontend/src/components/week/WeekPicker.test.tsx
// Plan 02-02 Task 3 — locks the 5-chip horizontal row, active chip highlighting,
// and chip→onChange semantics. The popover calendar is exercised lightly because
// react-day-picker rendering needs more setup; we just verify the trigger button.

import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';

import { WeekPicker } from '@/components/week/WeekPicker';

describe('WeekPicker', () => {
  it('renders 5 chips (current ± 2 weeks)', () => {
    render(<WeekPicker value="2026-05-04" onChange={() => {}} />);
    // Chip buttons + popover trigger button = 6 total. The chip group is identified
    // by its aria-label "Settimana corrente".
    const chipsGroup = screen.getByRole('group', {
      name: 'Settimana corrente',
    });
    const chipButtons = chipsGroup.querySelectorAll('button');
    // 5 chips + 1 popover trigger button
    expect(chipButtons.length).toBe(6);
  });

  it('marks the current week chip with aria-current=date', () => {
    render(<WeekPicker value="2026-05-04" onChange={() => {}} />);
    const active = screen.getByRole('button', { current: 'date' });
    expect(active.getAttribute('data-active')).toBe('true');
  });

  it('invokes onChange with the new YYYY-MM-DD when a different chip is clicked', () => {
    const onChange = vi.fn();
    render(<WeekPicker value="2026-05-04" onChange={onChange} />);
    const chipsGroup = screen.getByRole('group', {
      name: 'Settimana corrente',
    });
    const chipButtons = chipsGroup.querySelectorAll('button');
    // Click the LAST chip button = current + 2 weeks = 2026-05-18
    fireEvent.click(chipButtons[4] as HTMLButtonElement);
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith('2026-05-18');
  });

  it('does NOT invoke onChange when active chip is clicked', () => {
    const onChange = vi.fn();
    render(<WeekPicker value="2026-05-04" onChange={onChange} />);
    const active = screen.getByRole('button', { current: 'date' });
    fireEvent.click(active);
    expect(onChange).not.toHaveBeenCalled();
  });

  it('exposes a jump-to-date trigger button with italian aria-label', () => {
    render(<WeekPicker value="2026-05-04" onChange={() => {}} />);
    const jump = screen.getByRole('button', {
      name: "Scegli un'altra settimana",
    });
    expect(jump).toBeInTheDocument();
    // 44×44 hit target
    expect(jump.className).toContain('w-11');
    expect(jump.className).toContain('h-11');
  });
});
