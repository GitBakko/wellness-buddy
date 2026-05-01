// frontend/src/tests/unit/plans/PlanDiffView.test.tsx
// Plan 04 Task 3: section-level diff renders 3 buckets with italian section labels.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { PlanDiffView } from '@/components/plans/PlanDiffView';
import { copy } from '@/i18n/copy.it';

describe('PlanDiffView', () => {
  it('renders the three diff sections with italian labels', () => {
    render(
      <PlanDiffView
        diff={{
          added: ['dinners'],
          removed: ['lunches'],
          changed: ['breakfast'],
        }}
      />,
    );

    expect(screen.getByText(copy.plans.diffHeading)).toBeInTheDocument();
    expect(screen.getByText(copy.plans.diffAddedHeading)).toBeInTheDocument();
    expect(screen.getByText(copy.plans.diffRemovedHeading)).toBeInTheDocument();
    expect(screen.getByText(copy.plans.diffChangedHeading)).toBeInTheDocument();

    // Italian section labels (UI-SPEC SECTION_LABELS)
    expect(screen.getByText('Cene')).toBeInTheDocument();
    expect(screen.getByText('Pranzi')).toBeInTheDocument();
    expect(screen.getByText('Colazione')).toBeInTheDocument();
  });

  it('renders empty state when no diff', () => {
    render(<PlanDiffView diff={{ added: [], removed: [], changed: [] }} />);
    expect(screen.getByText(copy.plans.diffEmpty)).toBeInTheDocument();
  });

  it('only shows present buckets', () => {
    render(<PlanDiffView diff={{ added: ['dinners'], removed: [], changed: [] }} />);
    expect(screen.getByText(copy.plans.diffAddedHeading)).toBeInTheDocument();
    expect(screen.queryByText(copy.plans.diffRemovedHeading)).not.toBeInTheDocument();
    expect(screen.queryByText(copy.plans.diffChangedHeading)).not.toBeInTheDocument();
  });
});
