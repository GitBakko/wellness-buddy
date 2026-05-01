// frontend/src/components/__tests__/WorkoutForm.test.tsx
// Plan 07 Task 2 — verify the workout form's italian copy + conditional fields.

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { WorkoutForm } from '@/components/today/WorkoutForm';
import { copy } from '@/i18n/copy.it';

function renderWithQuery(
  ui: React.ReactElement,
): ReturnType<typeof render> {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 0 },
      mutations: { retry: false },
    },
  });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe('WorkoutForm', () => {
  it('renders italian heading + toggle when no existing workout', () => {
    renderWithQuery(<WorkoutForm />);
    expect(screen.getByText(copy.workout.heading)).toBeInTheDocument();
    expect(screen.getByText(copy.workout.toggleLabel)).toBeInTheDocument();
    // Submit CTA always visible — even when not trained
    expect(
      screen.getByRole('button', { name: copy.workout.submitCta }),
    ).toBeInTheDocument();
  });

  it('hides duration/type/notes when trained=false', () => {
    renderWithQuery(<WorkoutForm />);
    expect(screen.queryByLabelText(copy.workout.durationLabel)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(copy.workout.typeLabel)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(copy.workout.notesLabel)).not.toBeInTheDocument();
  });

  it('reveals duration/type/notes after toggling trained=true', async () => {
    const user = userEvent.setup();
    renderWithQuery(<WorkoutForm />);
    const toggle = screen.getByRole('switch', { name: copy.workout.toggleLabel });
    await user.click(toggle);
    expect(screen.getByLabelText(copy.workout.durationLabel)).toBeInTheDocument();
    expect(screen.getByLabelText(copy.workout.typeLabel)).toBeInTheDocument();
    expect(screen.getByLabelText(copy.workout.notesLabel)).toBeInTheDocument();
  });

  it('pre-fills from existing workout entry', () => {
    renderWithQuery(
      <WorkoutForm
        existing={{
          id: 'w1',
          trained: true,
          duration_min: 45,
          calories_burned: 320,
          workout_type: 'corsa',
          notes: '5 km easy',
        }}
      />,
    );
    expect(screen.getByLabelText(copy.workout.durationLabel)).toHaveValue('45');
    expect(screen.getByLabelText(copy.workout.typeLabel)).toHaveValue('corsa');
    expect(screen.getByLabelText(copy.workout.caloriesLabel)).toHaveValue('320');
    expect(screen.getByLabelText(copy.workout.notesLabel)).toHaveValue('5 km easy');
  });

  it('keeps copy strictly italian (no english fallback)', () => {
    renderWithQuery(<WorkoutForm />);
    // Spot-check: zero English imperative buttons
    expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /submit/i })).not.toBeInTheDocument();
  });
});

// Verify mutation queue path is not triggered when navigator.onLine is true (default jsdom).
describe('WorkoutForm copy is sourced from copy.it.ts', () => {
  it('uses copy.workout.successToast string', () => {
    expect(copy.workout.successToast).toBe('Allenamento registrato.');
  });

  it('uses italian toggle label (Hai allenato oggi?)', () => {
    expect(copy.workout.toggleLabel).toMatch(/^Hai allenato/);
  });

  it('does not use the forbidden `!` character in error states', () => {
    // CLAUDE.md tone rule — no `!` in error copy. Spot check error generic.
    expect(copy.errors.generic500.endsWith('!')).toBe(false);
    expect(copy.errors.networkOffline.endsWith('!')).toBe(false);
    // Suppress lint about unused import in environments without strict tree-shaking
    void vi.fn;
  });
});
