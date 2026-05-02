// frontend/src/components/week/DayCompletionStrip.tsx
// Plan 02-02 — 7-day completion strip below WeeklyMacroRing.
//
// UI-SPEC §6.2 anatomy:
//   ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐
//   │ Lun │ Mar │ Mer │ Gio │ Ven │ Sab │ Dom │   ← Plus Jakarta 600 11px caption
//   ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤
//   │ ███ │ ███ │ ▒▒▒ │ □□□ │ ─── │ □□□ │ □□□ │   ← 8px-tall pills, 8px gap
//   └─────┴─────┴─────┴─────┴─────┴─────┴─────┘
//
//   Pill colors:
//     leaf-500       — all 4 meals done
//     leaf-200       — 1-3 meals done (partial)
//     neutral-100    — planned (0 done, has plan)
//     neutral-200    outline — no plan
//
// All copy from copy.it.ts week.dayLabels; all colors via @theme tokens.

import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';

type DayState = 'done' | 'partial' | 'planned' | 'blank';

export interface DayCompletion {
  /** 0=Mon..6=Sun */
  dayOfWeek: number;
  /** Number of meals completed today. */
  completedCount: number;
  /** Total planned meals (typically 4 — breakfast/lunch/dinner/snack). */
  totalCount: number;
}

const DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as const;

function classifyDay(d: DayCompletion): DayState {
  if (d.totalCount === 0) return 'blank';
  if (d.completedCount === 0) return 'planned';
  if (d.completedCount >= d.totalCount) return 'done';
  return 'partial';
}

function pillStyleFor(state: DayState): React.CSSProperties {
  switch (state) {
    case 'done':
      return { background: 'var(--color-leaf-500)' };
    case 'partial':
      return { background: 'var(--color-leaf-200)' };
    case 'planned':
      return { background: 'var(--color-neutral-100)' };
    case 'blank':
      return {
        background: 'transparent',
        border: '1px solid var(--color-neutral-200)',
      };
  }
}

function ariaLabelFor(d: DayCompletion, state: DayState): string {
  const dayLabel = copy.week.dayLabels[DAY_KEYS[d.dayOfWeek]] ?? '';
  switch (state) {
    case 'done':
      return `${dayLabel}: ${copy.week.completionStripDayDone}`;
    case 'partial':
      return `${dayLabel}: ${copy.week.completionStripDayPartial
        .replace('{done}', String(d.completedCount))
        .replace('{total}', String(d.totalCount))}`;
    case 'planned':
      return `${dayLabel}: ${copy.week.completionStripDayPlanned}`;
    case 'blank':
      return `${dayLabel}: ${copy.week.completionStripDayBlank}`;
  }
}

export interface DayCompletionStripProps {
  days: DayCompletion[];
}

export function DayCompletionStrip({
  days,
}: DayCompletionStripProps): React.ReactElement {
  // Always render exactly 7 day cells, sorted by dayOfWeek.
  const sorted = [...days].sort((a, b) => a.dayOfWeek - b.dayOfWeek);
  return (
    <div className="grid grid-cols-7 gap-[var(--spacing-2)] w-full">
      {sorted.map((d) => {
        const state = classifyDay(d);
        const dayLabel = copy.week.dayLabels[DAY_KEYS[d.dayOfWeek]] ?? '';
        const aria = ariaLabelFor(d, state);
        return (
          <div
            key={d.dayOfWeek}
            className="flex flex-col items-center gap-[var(--spacing-1)]"
            aria-label={aria}
            data-state={state}
          >
            <span
              aria-hidden="true"
              className={cn(
                'text-[color:var(--color-text-muted)]',
                'font-semibold uppercase tracking-[0.04em]',
              )}
              style={{ fontSize: '0.6875rem' }}
            >
              {dayLabel.slice(0, 3)}
            </span>
            <span
              aria-hidden="true"
              className="w-full h-2 rounded-[var(--radius-pill)]"
              style={pillStyleFor(state)}
            />
          </div>
        );
      })}
    </div>
  );
}
