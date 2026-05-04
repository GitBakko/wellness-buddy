// frontend/src/components/shopping/__tests__/ShoppingViewToggle.test.tsx
// Plan 02-05 — locks the segmented control "Per categoria" / "Per giorno".

import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';

import { ShoppingViewToggle } from '@/components/shopping/ShoppingViewToggle';

describe('ShoppingViewToggle', () => {
  it('renders both Italian buttons inside a labelled group', () => {
    render(<ShoppingViewToggle value="category" onChange={() => {}} />);
    const group = screen.getByRole('group', { name: /vista lista spesa/i });
    expect(group).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Per categoria' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Per giorno' })).toBeInTheDocument();
  });

  it('marks the active button via aria-pressed and data-active', () => {
    render(<ShoppingViewToggle value="category" onChange={() => {}} />);
    const cat = screen.getByRole('button', { name: 'Per categoria' });
    const day = screen.getByRole('button', { name: 'Per giorno' });
    expect(cat.getAttribute('aria-pressed')).toBe('true');
    expect(cat.getAttribute('data-active')).toBe('true');
    expect(day.getAttribute('aria-pressed')).toBe('false');
    expect(day.getAttribute('data-active')).toBeNull();
  });

  it('invokes onChange with new view when inactive button clicked', () => {
    const onChange = vi.fn();
    render(<ShoppingViewToggle value="category" onChange={onChange} />);
    fireEvent.click(screen.getByRole('button', { name: 'Per giorno' }));
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith('day');
  });
});
