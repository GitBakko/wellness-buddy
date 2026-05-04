// frontend/src/components/shopping/__tests__/ShoppingCategorySection.test.tsx
// Plan 02-05 — locks the collapsible header + category icon resolution +
// item-count badge + onToggleItem propagation.

import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';

import { ShoppingCategorySection } from '@/components/shopping/ShoppingCategorySection';
import type { ShoppingItem } from '@/services/shopping';

const items: ShoppingItem[] = [
  {
    canonical_name: 'yogurt greco',
    name_display: 'Yogurt Greco',
    amount: 200,
    unit: 'g',
    quantity_it: '200 g',
    category: 'Frigo & Freschi',
    checked: false,
    sources: ['breakfast_d0'],
  },
  {
    canonical_name: 'salmone',
    name_display: 'Salmone',
    amount: 200,
    unit: 'g',
    quantity_it: '200 g',
    category: 'Frigo & Freschi',
    checked: true,
    sources: ['dinner_d0'],
  },
];

describe('ShoppingCategorySection', () => {
  it('renders category name + count badge as N/M (checked/total)', () => {
    render(
      <ShoppingCategorySection
        name="Frigo & Freschi"
        items={items}
        onToggleItem={() => {}}
      />,
    );
    expect(screen.getByRole('heading', { level: 3, name: /frigo & freschi/i })).toBeInTheDocument();
    expect(screen.getByLabelText('1 di 2')).toHaveTextContent('1/2');
  });

  it('renders one ShoppingItemRow per item', () => {
    render(
      <ShoppingCategorySection
        name="Frigo & Freschi"
        items={items}
        onToggleItem={() => {}}
      />,
    );
    expect(screen.getAllByRole('checkbox')).toHaveLength(items.length);
  });

  it('propagates onToggleItem with the item + new state', () => {
    const onToggleItem = vi.fn();
    render(
      <ShoppingCategorySection
        name="Frigo & Freschi"
        items={items}
        onToggleItem={onToggleItem}
      />,
    );
    const yogurtCheckbox = screen.getByRole('checkbox', { name: /yogurt.*da prendere/i });
    fireEvent.click(yogurtCheckbox);
    expect(onToggleItem).toHaveBeenCalledTimes(1);
    expect(onToggleItem.mock.calls[0][0]?.canonical_name).toBe('yogurt greco');
    expect(onToggleItem.mock.calls[0][1]).toBe(true);
  });

  it('renders empty state copy when items list is empty', () => {
    render(
      <ShoppingCategorySection
        name="Integratori"
        items={[]}
        onToggleItem={() => {}}
      />,
    );
    expect(screen.getByText('Niente da prendere qui.')).toBeInTheDocument();
  });

  it('uses native <details> for collapse — opens by default', () => {
    const { container } = render(
      <ShoppingCategorySection
        name="Dispensa"
        items={items}
        onToggleItem={() => {}}
      />,
    );
    const details = container.querySelector('details');
    expect(details).not.toBeNull();
    expect(details!.hasAttribute('open')).toBe(true);
    expect(details!.getAttribute('data-category')).toBe('Dispensa');
  });
});
