// frontend/src/components/family/__tests__/SharedBadge.test.tsx
// Plan 02-07 — locks SharedBadge anatomy + ARIA + Italian tooltip.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { SharedBadge } from '@/components/family/SharedBadge';

describe('SharedBadge (Plan 02-07)', () => {
  it('renders partner name in pill + Italian aria-label', () => {
    render(<SharedBadge partnerName="Marta" updatedAt={null} />);
    const badge = screen.getByTestId('shared-badge');
    expect(badge).toBeInTheDocument();
    // The visible label shows partner name
    expect(screen.getByText('Marta')).toBeInTheDocument();
    // ARIA label uses the localised "Condiviso con {partnerName}"
    expect(badge).toHaveAttribute('aria-label', 'Condiviso con Marta');
  });

  it('renders an UsersThree Phosphor SVG (decorative — aria-hidden)', () => {
    const { container } = render(<SharedBadge partnerName="Marta" updatedAt={null} />);
    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    expect(svg?.getAttribute('aria-hidden')).toBe('true');
  });

  it('truncates very long partner names via truncate class', () => {
    const longName = 'M'.repeat(60);
    render(<SharedBadge partnerName={longName} updatedAt={null} />);
    const span = screen.getByText(longName);
    expect(span.className).toMatch(/truncate/);
    expect(span.className).toMatch(/max-w-\[12ch\]/);
  });
});
