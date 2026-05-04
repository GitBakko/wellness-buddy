// frontend/src/components/plans/PlanDiffView.tsx
// Plan 04 Task 3 — section-level diff view (PLAN-09, UI-SPEC §6.4).
//
// Three buckets: aggiunte / rimosse / modificate. Buckets only appear if they
// have entries — empty state is a single muted line. Section labels are the
// italian translations from copy.plans.heading namespace mapping.

import { Card } from '@/components/ui/card';
import { copy } from '@/i18n/copy.it';
import type { PlanDiffResponse } from '@/services/plans';

const SECTION_LABELS: Record<string, string> = {
  personal_data: 'Dati personali',
  macro_target: 'Calcolo calorico e macro',
  daily_structure: 'Struttura giornaliera',
  breakfast: 'Colazione',
  lunches: 'Pranzi',
  dinners: 'Cene',
  snacks: 'Spuntini',
  supplements: 'Supplementazione',
  weight_projection: 'Proiezione peso',
  rules: 'Regole fondamentali',
};

function labelize(key: string): string {
  return SECTION_LABELS[key] ?? key;
}

interface PlanDiffViewProps {
  diff: PlanDiffResponse;
}

export function PlanDiffView({ diff }: PlanDiffViewProps): React.ReactElement {
  const total = diff.added.length + diff.removed.length + diff.changed.length;
  // First plan upload: backend has_active_plan=false. Use neutral heading
  // and skip the added/removed/changed bucket layout (everything is "added"
  // by definition — labelling that as "Differenze" is misleading).
  const isFirstPlan = !diff.has_active_plan;

  return (
    <Card
      className="flex flex-col gap-[var(--spacing-4)] p-[var(--spacing-4)] sm:p-[var(--spacing-6)]"
      variant="flat"
    >
      <h2 className="text-[length:var(--text-heading)] font-semibold leading-[var(--leading-heading)] text-[var(--color-text)]">
        {isFirstPlan ? copy.plans.firstPlanHeading : copy.plans.diffHeading}
      </h2>

      {total === 0 && (
        <p className="text-[length:var(--text-base)] text-[var(--color-text-muted)]">
          {copy.plans.diffEmpty}
        </p>
      )}

      {isFirstPlan && diff.added.length > 0 && (
        <ul className="flex flex-col gap-[var(--spacing-1)] pl-[var(--spacing-5)] list-disc text-[length:var(--text-base)] text-[var(--color-text)]">
          {diff.added.map((k) => (
            <li key={`section-${k}`}>{labelize(k)}</li>
          ))}
        </ul>
      )}

      {!isFirstPlan && diff.added.length > 0 && (
        <section className="flex flex-col gap-[var(--spacing-2)]">
          <h3 className="text-[length:var(--text-base)] font-semibold text-[var(--color-success)]">
            {copy.plans.diffAddedHeading}
          </h3>
          <ul className="flex flex-col gap-[var(--spacing-1)] pl-[var(--spacing-5)] list-disc text-[length:var(--text-base)] text-[var(--color-text)]">
            {diff.added.map((k) => (
              <li key={`added-${k}`}>{labelize(k)}</li>
            ))}
          </ul>
        </section>
      )}

      {!isFirstPlan && diff.removed.length > 0 && (
        <section className="flex flex-col gap-[var(--spacing-2)]">
          <h3 className="text-[length:var(--text-base)] font-semibold text-[var(--color-destructive)]">
            {copy.plans.diffRemovedHeading}
          </h3>
          <ul className="flex flex-col gap-[var(--spacing-1)] pl-[var(--spacing-5)] list-disc text-[length:var(--text-base)] text-[var(--color-text)]">
            {diff.removed.map((k) => (
              <li key={`removed-${k}`}>{labelize(k)}</li>
            ))}
          </ul>
        </section>
      )}

      {!isFirstPlan && diff.changed.length > 0 && (
        <section className="flex flex-col gap-[var(--spacing-2)]">
          <h3 className="text-[length:var(--text-base)] font-semibold text-[var(--color-coral-700)]">
            {copy.plans.diffChangedHeading}
          </h3>
          <ul className="flex flex-col gap-[var(--spacing-1)] pl-[var(--spacing-5)] list-disc text-[length:var(--text-base)] text-[var(--color-text)]">
            {diff.changed.map((k) => (
              <li key={`changed-${k}`}>{labelize(k)}</li>
            ))}
          </ul>
        </section>
      )}
    </Card>
  );
}
