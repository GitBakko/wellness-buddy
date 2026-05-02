// frontend/src/components/week/VariantSelector.test.tsx
// Plan 02-02 Task 3 — locks the trigger pill, dropdown menu, active-dot indicator,
// and onChange firing semantics for the 3 variant options.

import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { VariantSelector } from '@/components/week/VariantSelector';

describe('VariantSelector', () => {
  it('renders trigger pill with active variant label', () => {
    render(
      <VariantSelector
        value="A"
        onChange={() => {}}
        mealLabel="Pranzo"
      />,
    );
    const trigger = screen.getByRole('button', {
      name: 'Cambia variante per Pranzo',
    });
    expect(trigger).toBeInTheDocument();
    expect(trigger).toHaveTextContent('Opzione A');
    expect(trigger.getAttribute('data-variant')).toBe('A');
  });

  it('opens dropdown with 3 menu items when trigger clicked', async () => {
    const user = userEvent.setup();
    render(
      <VariantSelector value="A" onChange={() => {}} mealLabel="Cena" />,
    );
    const trigger = screen.getByRole('button', {
      name: 'Cambia variante per Cena',
    });
    await user.click(trigger);
    const items = await screen.findAllByRole('menuitem');
    expect(items).toHaveLength(3);
    const itemLabels = items.map((i) => i.textContent ?? '');
    expect(itemLabels.some((l) => l.includes('Opzione A'))).toBe(true);
    expect(itemLabels.some((l) => l.includes('Opzione B'))).toBe(true);
    expect(itemLabels.some((l) => l.includes('Pasta speciale'))).toBe(true);
  });

  it('marks active variant with aria-current=true', async () => {
    const user = userEvent.setup();
    render(
      <VariantSelector value="B" onChange={() => {}} mealLabel="Cena" />,
    );
    await user.click(
      screen.getByRole('button', { name: 'Cambia variante per Cena' }),
    );
    const items = await screen.findAllByRole('menuitem');
    const active = items.find(
      (el) => el.getAttribute('aria-current') === 'true',
    );
    expect(active).toBeDefined();
    expect(active?.textContent).toContain('Opzione B');
  });

  it('invokes onChange with new variant key when a different option is selected', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <VariantSelector value="A" onChange={onChange} mealLabel="Cena" />,
    );
    await user.click(
      screen.getByRole('button', { name: 'Cambia variante per Cena' }),
    );
    const items = await screen.findAllByRole('menuitem');
    const optionB = items.find((el) => (el.textContent ?? '').includes('Opzione B'));
    expect(optionB).toBeDefined();
    await user.click(optionB!);
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith('B');
  });

  it('does NOT invoke onChange when active variant is re-selected', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <VariantSelector value="A" onChange={onChange} mealLabel="Pranzo" />,
    );
    await user.click(
      screen.getByRole('button', { name: 'Cambia variante per Pranzo' }),
    );
    const items = await screen.findAllByRole('menuitem');
    const optionA = items.find((el) => el.getAttribute('aria-current') === 'true');
    expect(optionA).toBeDefined();
    await user.click(optionA!);
    expect(onChange).not.toHaveBeenCalled();
  });

  it('renders compact macro preview when macroPreviews provided', async () => {
    const user = userEvent.setup();
    render(
      <VariantSelector
        value="A"
        onChange={() => {}}
        mealLabel="Cena"
        macroPreviews={{
          A: { kcal: 720, protein_g: 28, carbs_g: 90, fat_g: 18 },
        }}
      />,
    );
    await user.click(
      screen.getByRole('button', { name: 'Cambia variante per Cena' }),
    );
    // Wait for menu to open then assert macro chip
    await screen.findAllByRole('menuitem');
    const previewMatch = screen.queryByText(/720 kcal · P 28 · C 90 · F 18/);
    expect(previewMatch).not.toBeNull();
  });

  // Disabled-state assertion uses synchronous DOM (no menu open needed).
  it('respects disabled prop on the trigger', () => {
    render(
      <VariantSelector
        value="A"
        onChange={() => {}}
        mealLabel="Pranzo"
        disabled
      />,
    );
    const trigger = screen.getByRole('button', {
      name: 'Cambia variante per Pranzo',
    });
    expect(trigger).toBeDisabled();
    // fireEvent stays here as a sanity check that the test util import works
    fireEvent.click(trigger);
  });
});
