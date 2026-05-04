// frontend/src/components/shopping/__tests__/ShoppingItemRow.test.tsx
// Plan 02-05 — locks checkbox semantics + checked-state visuals.

import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';

import { ShoppingItemRow } from '@/components/shopping/ShoppingItemRow';
import type { ShoppingItem } from '@/services/shopping';

const baseItem: ShoppingItem = {
  canonical_name: 'pomodoro',
  name_display: 'Pomodoro',
  amount: 200,
  unit: 'g',
  quantity_it: '200 g',
  category: 'Frutta & Verdura',
  checked: false,
  sources: ['lunch_d0'],
};

describe('ShoppingItemRow', () => {
  it('renders name + quantity + accessible aria label', () => {
    render(<ShoppingItemRow item={baseItem} onToggle={() => {}} />);
    expect(screen.getByText('Pomodoro')).toBeInTheDocument();
    expect(screen.getByText('200 g')).toBeInTheDocument();
    const checkbox = screen.getByRole('checkbox', {
      name: /pomodoro.*da prendere/i,
    });
    expect(checkbox).toBeInTheDocument();
  });

  it('calls onToggle(true) when unchecked checkbox is clicked', () => {
    const onToggle = vi.fn();
    render(<ShoppingItemRow item={baseItem} onToggle={onToggle} />);
    fireEvent.click(screen.getByRole('checkbox'));
    expect(onToggle).toHaveBeenCalledWith(true);
  });

  it('reflects checked state in DOM (data-checked) when item.checked=true', () => {
    render(<ShoppingItemRow item={{ ...baseItem, checked: true }} onToggle={() => {}} />);
    const li = screen.getByRole('listitem');
    expect(li.getAttribute('data-checked')).toBe('true');
    const checkbox = screen.getByRole('checkbox', { name: /pomodoro.*preso/i });
    expect(checkbox).toBeInTheDocument();
  });

  it('renders optional context caption', () => {
    render(
      <ShoppingItemRow
        item={baseItem}
        contextCaption="PRANZO · lunedì"
        onToggle={() => {}}
      />,
    );
    expect(screen.getByText('PRANZO · lunedì')).toBeInTheDocument();
  });
});
