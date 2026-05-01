// frontend/src/components/workout/WorkoutHistoryTable.tsx
// Phase 1 list view of workout entries grouped by month. Italian month names via
// Intl.DateTimeFormat — no manual formatting (UI rule 11).

import { Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { copy } from '@/i18n/copy.it';
import { italianDateLong } from '@/lib/format';
import {
  useDeleteWorkout,
  useWorkouts,
  type WorkoutLog,
} from '@/services/workout';

const MONTH_FMT = new Intl.DateTimeFormat('it-IT', {
  year: 'numeric',
  month: 'long',
});

function groupByMonth(rows: WorkoutLog[]): Map<string, WorkoutLog[]> {
  const groups = new Map<string, WorkoutLog[]>();
  for (const row of rows) {
    const key = MONTH_FMT.format(new Date(row.date));
    const bucket = groups.get(key) ?? [];
    bucket.push(row);
    groups.set(key, bucket);
  }
  return groups;
}

function describeWorkout(w: WorkoutLog): string {
  if (!w.trained) {
    return 'Riposo';
  }
  const parts: string[] = [];
  if (w.workout_type) parts.push(w.workout_type);
  if (w.duration_min != null) parts.push(`${w.duration_min} min`);
  return parts.join(' · ') || 'Allenamento';
}

export function WorkoutHistoryTable(): React.ReactElement {
  const { data, isLoading } = useWorkouts();
  const del = useDeleteWorkout();

  async function onDelete(row: WorkoutLog): Promise<void> {
    const confirmMsg = copy.workout.deleteConfirm.replace(
      '{data}',
      italianDateLong(new Date(row.date)),
    );
    if (!window.confirm(confirmMsg)) return;
    try {
      await del.mutateAsync(row.id);
      toast.success('Allenamento eliminato.');
    } catch {
      toast.error(copy.errors.generic500);
    }
  }

  if (isLoading) {
    return <p className="text-[color:var(--color-text-muted)]">…</p>;
  }
  if (!data || data.length === 0) {
    return (
      <p className="text-[color:var(--color-text-muted)]">
        {copy.today.emptyDayBlank.body}
      </p>
    );
  }
  const grouped = groupByMonth(data);

  return (
    <div className="flex flex-col gap-[var(--spacing-4)]" aria-label="Storico allenamenti">
      {Array.from(grouped.entries()).map(([month, rows]) => (
        <section key={month} className="flex flex-col gap-[var(--spacing-2)]">
          <h3 className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] uppercase tracking-wide capitalize">
            {month}
          </h3>
          <ul className="flex flex-col gap-[var(--spacing-2)]">
            {rows.map((row) => (
              <li key={row.id}>
                <Card className="p-[var(--spacing-3)] flex items-center justify-between gap-[var(--spacing-3)]">
                  <div className="flex flex-col">
                    <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] capitalize">
                      {italianDateLong(new Date(row.date))}
                    </span>
                    <span className="text-[var(--text-base)] text-[color:var(--color-text)]">
                      {describeWorkout(row)}
                    </span>
                    {row.notes && (
                      <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)]">
                        {row.notes}
                      </span>
                    )}
                  </div>
                  <Button
                    size="icon"
                    variant="ghost"
                    aria-label={copy.workout.deleteCta}
                    onClick={() => void onDelete(row)}
                  >
                    <Trash2 aria-hidden="true" />
                  </Button>
                </Card>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
