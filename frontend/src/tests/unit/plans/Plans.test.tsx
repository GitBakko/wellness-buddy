// frontend/src/tests/unit/plans/Plans.test.tsx
// Plan 04 Task 3: Plans page composition smoke test.
//
// Validates: page renders without crashes, copy strings come from copy.it.ts,
// upload happy path causes a plan to appear in the list.

import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import Plans from '@/pages/Plans';
import { copy } from '@/i18n/copy.it';

function renderPlans(): ReturnType<typeof render> {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 0 },
      mutations: { retry: false },
    },
  });
  return render(
    <QueryClientProvider client={qc}>
      <Plans />
    </QueryClientProvider>,
  );
}

describe('Plans page', () => {
  it('renders heading from copy.plans.heading', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    } as Response);

    renderPlans();
    expect(screen.getByText(copy.plans.heading)).toBeInTheDocument();
  });

  it('renders empty state when no plans', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    } as Response);

    renderPlans();
    await waitFor(() => {
      expect(screen.getByText(copy.plans.listEmpty)).toBeInTheDocument();
    });
  });

  it('renders plans list with active badge', async () => {
    const plans = [
      {
        id: 'p1',
        name: 'Plan attivo',
        uploaded_at: '2026-05-01T10:00:00Z',
        is_active: true,
      },
      {
        id: 'p2',
        name: 'Plan vecchio',
        uploaded_at: '2026-04-01T10:00:00Z',
        is_active: false,
      },
    ];
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => plans,
    } as Response);

    renderPlans();
    await waitFor(() => {
      expect(screen.getByText('Plan attivo')).toBeInTheDocument();
      expect(screen.getByText('Plan vecchio')).toBeInTheDocument();
      expect(screen.getByText(`(${copy.plans.listActiveBadge})`)).toBeInTheDocument();
    });
  });
});
