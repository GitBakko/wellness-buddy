// frontend/src/components/today/DayStatusIndicator.tsx
// UI-SPEC §6.4 — pill indicator for day status.
// Plan 01-09 — switched from lucide-react to Phosphor via the icon facade.
//
// Color rules (UI-SPEC §6.4 — verbatim):
//   completed → leaf-500 / leaf-soft pill (success)
//   partial   → neutral half-tone (text-muted)
//   planned   → neutral outline
//   NEVER red — even when nothing logged. Empty state is "planned" (neutral),
//   never failure.

import { CheckCircle, Circle } from '@/components/icons';

export type DayStatus = 'planned' | 'partial' | 'completed';

const LABEL: Record<DayStatus, string> = {
  completed: 'Completato',
  partial: 'Parziale',
  planned: 'Pianificato',
};

const PILL_BASE =
  'inline-flex items-center gap-[var(--spacing-1)] px-[var(--spacing-3)] ' +
  'py-[var(--spacing-1)] rounded-[var(--radius-pill)] text-[var(--text-caption)] font-semibold';

export function DayStatusIndicator({
  status,
}: {
  status: DayStatus;
}): React.ReactElement {
  if (status === 'completed') {
    return (
      <span
        className={`${PILL_BASE} bg-[var(--color-leaf-100)] text-[color:var(--color-leaf-700)]`}
        role="status"
        aria-label={LABEL.completed}
      >
        <CheckCircle size={16} weight="fill" aria-hidden="true" /> {LABEL.completed}
      </span>
    );
  }
  if (status === 'partial') {
    return (
      <span
        className={`${PILL_BASE} bg-[var(--color-surface-muted)] text-[color:var(--color-text-muted)]`}
        role="status"
        aria-label={LABEL.partial}
      >
        <Circle size={16} weight="fill" aria-hidden="true" /> {LABEL.partial}
      </span>
    );
  }
  return (
    <span
      className={`${PILL_BASE} border border-[var(--color-border)] text-[color:var(--color-text-muted)]`}
      role="status"
      aria-label={LABEL.planned}
    >
      <Circle size={16} weight="regular" aria-hidden="true" /> {LABEL.planned}
    </span>
  );
}
