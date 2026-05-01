// frontend/src/components/today/DayStatusIndicator.tsx
// UI-SPEC §6.4 — pill indicator for day status.
//
// Color rules (UI-SPEC §6.4 — verbatim):
//   completed → leaf-green (success)
//   partial   → neutral half-tone (text-muted)
//   planned   → neutral outline
//   NEVER red — even when nothing logged. Empty state is "planned" (neutral),
//   never failure.

import { CheckCircle2, Circle, CircleDot } from 'lucide-react';

export type DayStatus = 'planned' | 'partial' | 'completed';

const LABEL: Record<DayStatus, string> = {
  completed: 'Completato',
  partial: 'Parziale',
  planned: 'Pianificato',
};

const PILL_BASE =
  'inline-flex items-center gap-[var(--spacing-1)] px-[var(--spacing-3)] ' +
  'py-[var(--spacing-1)] rounded-[var(--radius-pill)] text-[var(--text-caption)]';

export function DayStatusIndicator({
  status,
}: {
  status: DayStatus;
}): React.ReactElement {
  if (status === 'completed') {
    return (
      <span
        className={`${PILL_BASE} bg-[var(--color-success-bg)] text-[color:var(--color-success)]`}
        role="status"
        aria-label={LABEL.completed}
      >
        <CheckCircle2 size={16} aria-hidden="true" /> {LABEL.completed}
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
        <CircleDot size={16} aria-hidden="true" /> {LABEL.partial}
      </span>
    );
  }
  return (
    <span
      className={`${PILL_BASE} border border-[var(--color-border)] text-[color:var(--color-text-muted)]`}
      role="status"
      aria-label={LABEL.planned}
    >
      <Circle size={16} aria-hidden="true" /> {LABEL.planned}
    </span>
  );
}
