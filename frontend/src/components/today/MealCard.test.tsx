// frontend/src/components/today/MealCard.test.tsx
// Plan 01-09 Task 2 — locks photo render path, gradient placeholder fallback,
// and Phosphor SVG icon usage (no emoji, no <img> for slot indicator).

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { MealCard } from '@/components/today/MealCard';
import type { TodayMeal } from '@/services/today';

const baseMeal: TodayMeal = {
  meal_type: 'breakfast',
  variant_key: 'default',
  title: 'Yogurt greco, granola, mirtilli',
  macros: { kcal: 380, protein_g: 22, carbs_g: 45, fat_g: 12 },
  completed: false,
  photo_url: null,
};

describe('MealCard (Plan 01-09)', () => {
  it('renders photo when photo_url is provided', () => {
    const meal: TodayMeal = {
      ...baseMeal,
      photo_url: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400',
    };
    const { container } = render(
      <MealCard meal={meal} onToggle={() => {}} />,
    );
    const img = container.querySelector('img');
    expect(img).not.toBeNull();
    expect(img?.getAttribute('src')).toContain('images.unsplash.com');
    expect(img?.getAttribute('loading')).toBe('lazy');
    expect(img?.getAttribute('width')).toBe('80');
    expect(img?.getAttribute('height')).toBe('80');
  });

  it('renders gradient placeholder div when photo_url is null', () => {
    const { container } = render(
      <MealCard meal={baseMeal} onToggle={() => {}} />,
    );
    const img = container.querySelector('img');
    // No <img> rendered, the placeholder is a div
    expect(img).toBeNull();
    // The placeholder div is aria-hidden so it doesn't pollute the tree.
    const placeholder = container.querySelector('div[aria-hidden="true"]');
    expect(placeholder).not.toBeNull();
    // Phosphor renders an SVG inside the placeholder for the slot icon.
    expect(placeholder?.querySelector('svg')).not.toBeNull();
  });

  it('uses a Phosphor SVG (not an <img> emoji) for the slot indicator', () => {
    const { container } = render(
      <MealCard meal={baseMeal} onToggle={() => {}} />,
    );
    // Slot icon must be an SVG element — verifies Phosphor facade is wired.
    const placeholder = container.querySelector('div[aria-hidden="true"]');
    const svg = placeholder?.querySelector('svg');
    expect(svg).not.toBeNull();
    expect(svg?.tagName.toLowerCase()).toBe('svg');
  });

  it('exposes ≥44×44 check button with italian aria-label when pending', () => {
    render(<MealCard meal={baseMeal} onToggle={() => {}} />);
    const btn = screen.getByRole('button', { name: 'Segna pasto' });
    expect(btn.className).toContain('w-11');
    expect(btn.className).toContain('h-11');
    expect(btn).not.toBeDisabled();
  });

  it('shows "Pasto registrato" aria-label + leaf-fill style when completed', () => {
    const completed: TodayMeal = { ...baseMeal, completed: true };
    render(<MealCard meal={completed} onToggle={() => {}} />);
    const btn = screen.getByRole('button', { name: 'Pasto registrato' });
    expect(btn).toBeDisabled();
    expect(btn.getAttribute('data-completed')).toBe('true');
  });

  it('invokes onToggle when pending check button is clicked', () => {
    const onToggle = vi.fn();
    render(<MealCard meal={baseMeal} onToggle={onToggle} />);
    const btn = screen.getByRole('button', { name: 'Segna pasto' });
    btn.click();
    expect(onToggle).toHaveBeenCalledTimes(1);
  });

  it('does NOT invoke onToggle when meal is already completed', () => {
    const onToggle = vi.fn();
    const completed: TodayMeal = { ...baseMeal, completed: true };
    render(<MealCard meal={completed} onToggle={onToggle} />);
    const btn = screen.getByRole('button', { name: 'Pasto registrato' });
    btn.click();
    expect(onToggle).not.toHaveBeenCalled();
  });
});
