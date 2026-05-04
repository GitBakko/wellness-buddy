// frontend/src/components/shopping/__tests__/EmptyStateShopping.test.tsx
// Plan 02-05 — locks the empty state heading, body, CTA, and routing target.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';

import { EmptyStateShopping } from '@/components/shopping/EmptyStateShopping';

describe('EmptyStateShopping', () => {
  it('renders heading + body + CTA from copy.it.ts shopping.* namespace', () => {
    render(
      <MemoryRouter>
        <EmptyStateShopping />
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: 'Nessuna spesa pianificata' })).toBeInTheDocument();
    expect(screen.getByText('Scegli le varianti settimanali per generare la lista.')).toBeInTheDocument();
    const cta = screen.getByRole('link', { name: 'Vai alla settimana' });
    expect(cta).toBeInTheDocument();
    expect(cta.getAttribute('href')).toBe('/settimana');
  });
});
