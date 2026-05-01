// frontend/src/components/today/WorkoutForm.tsx
// UI-SPEC §6.4 + §7.2 — Italian copy + Switch toggle + conditional fields.
//
// Behavior:
//   - "Hai allenato oggi?" Switch (copy.workout.toggleLabel)
//   - When trained=true: show duration_min, workout_type, calories_burned (optional),
//     notes (optional)
//   - When trained=false: only the toggle is shown (minimal payload accepted by backend)
//   - All copy from copy.it.ts (FND-09); all colors via tokens (UI-01)

import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { copy } from '@/i18n/copy.it';
import { useLogWorkout } from '@/services/workout';

/** Subset shape — matches both `WorkoutLog` and `TodayWorkout` (no `date` on the latter). */
interface ExistingWorkout {
  id: string;
  trained: boolean;
  duration_min: number | null;
  calories_burned: number | null;
  workout_type: string | null;
  notes: string | null;
}

interface Props {
  existing?: ExistingWorkout | null;
  todayIso?: string;
}

function defaultTodayIso(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function clampInt(value: string, max: number): number | null {
  const n = parseInt(value, 10);
  if (!Number.isFinite(n) || n < 0) return null;
  return Math.min(n, max);
}

const ERROR_DURATION = 'Indica una durata valida in minuti.';

export function WorkoutForm({ existing, todayIso }: Props): React.ReactElement {
  const log = useLogWorkout();
  const [trained, setTrained] = useState<boolean>(existing?.trained ?? false);
  const [duration, setDuration] = useState<string>(
    existing?.duration_min != null ? String(existing.duration_min) : '',
  );
  const [workoutType, setWorkoutType] = useState<string>(
    existing?.workout_type ?? '',
  );
  const [calories, setCalories] = useState<string>(
    existing?.calories_burned != null ? String(existing.calories_burned) : '',
  );
  const [notes, setNotes] = useState<string>(existing?.notes ?? '');
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    setError(null);
    let durationVal: number | null = null;
    if (trained && duration.trim() !== '') {
      durationVal = clampInt(duration, 24 * 60);
      if (durationVal == null) {
        setError(ERROR_DURATION);
        return;
      }
    }
    const caloriesVal = trained && calories.trim() !== '' ? clampInt(calories, 10000) : null;
    const date = todayIso ?? defaultTodayIso();
    try {
      await log.mutateAsync({
        date,
        trained,
        duration_min: durationVal,
        calories_burned: caloriesVal,
        workout_type: trained ? workoutType.trim() || null : null,
        notes: trained ? notes.trim() || null : null,
      });
      toast.success(copy.workout.successToast);
    } catch {
      toast.error(copy.errors.generic500);
    }
  }

  return (
    <Card
      className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-3)]"
      aria-label={copy.workout.heading}
    >
      <h2 className="text-[var(--text-base)] font-semibold text-[color:var(--color-text)]">
        {copy.workout.heading}
      </h2>
      <form onSubmit={onSubmit} className="flex flex-col gap-[var(--spacing-3)]" noValidate>
        <label className="inline-flex items-center justify-between gap-[var(--spacing-3)] min-h-11">
          <span className="text-[var(--text-base)] text-[color:var(--color-text)]">
            {copy.workout.toggleLabel}
          </span>
          <Switch checked={trained} onCheckedChange={setTrained} aria-label={copy.workout.toggleLabel} />
        </label>

        {trained && (
          <div className="flex flex-col gap-[var(--spacing-3)]">
            <div className="flex flex-col gap-[var(--spacing-1)]">
              <Label htmlFor="workout-duration">{copy.workout.durationLabel}</Label>
              <Input
                id="workout-duration"
                inputMode="numeric"
                value={duration}
                onChange={(e) => {
                  setDuration(e.target.value.replace(/[^0-9]/g, ''));
                  if (error) setError(null);
                }}
                aria-invalid={error ? true : undefined}
                aria-describedby={error ? 'workout-duration-error' : undefined}
              />
              {error && (
                <p
                  id="workout-duration-error"
                  role="alert"
                  className="inline-flex items-center gap-[var(--spacing-1)] text-[var(--text-caption)] text-[color:var(--color-destructive)]"
                >
                  <AlertCircle size={14} aria-hidden="true" />
                  {error}
                </p>
              )}
            </div>

            <div className="flex flex-col gap-[var(--spacing-1)]">
              <Label htmlFor="workout-type">{copy.workout.typeLabel}</Label>
              <Input
                id="workout-type"
                value={workoutType}
                onChange={(e) => setWorkoutType(e.target.value)}
                placeholder={copy.workout.typePlaceholder}
                autoComplete="off"
              />
            </div>

            <div className="flex flex-col gap-[var(--spacing-1)]">
              <Label htmlFor="workout-calories">{copy.workout.caloriesLabel}</Label>
              <Input
                id="workout-calories"
                inputMode="numeric"
                value={calories}
                onChange={(e) =>
                  setCalories(e.target.value.replace(/[^0-9]/g, ''))
                }
              />
              <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)]">
                {copy.workout.caloriesHelper}
              </span>
            </div>

            <div className="flex flex-col gap-[var(--spacing-1)]">
              <Label htmlFor="workout-notes">{copy.workout.notesLabel}</Label>
              <Textarea
                id="workout-notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <Button type="submit" disabled={log.isPending}>
            {copy.workout.submitCta}
          </Button>
        </div>
      </form>
    </Card>
  );
}
