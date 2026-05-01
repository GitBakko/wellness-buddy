// frontend/src/pages/Today.tsx
// Phase 1 deliverable — the page the user lands on after login.
//
// UI-SPEC §3.2 — ESCAPE HATCH: this is the ONLY place in src/ permitted to use
//   `--text-display-serif` (Instrument Serif 36px). The greeting <h1> uses it; nothing
//   else may. ESLint hex-ban + grep gate verify.
//
// Composition (mobile-first):
//   1. Greeting <h1>  ← Instrument Serif escape hatch
//   2. Date subline (italianDateLong)
//   3. MealCard list (from active plan parsed_json)
//   4. WeightQuickLog + WorkoutForm (responsive 2-col on md+)
//   5. AIWidget placeholder (Plan 06 — DO NOT modify, just render)

import { Link } from 'react-router';

import { AIWidget } from '@/components/ai/AIWidget';
import { MealCard } from '@/components/today/MealCard';
import { WeightQuickLog } from '@/components/today/WeightQuickLog';
import { WorkoutForm } from '@/components/today/WorkoutForm';
import { Skeleton } from '@/components/ui/skeleton';
import { copy } from '@/i18n/copy.it';
import { italianDateLong } from '@/lib/format';
import { useToday, useCompleteMeal } from '@/services/today';
import { useAuthStore } from '@/stores/auth';

function Greeting({
  period,
  username,
  isoDate,
}: {
  period: 'morning' | 'afternoon' | 'evening' | 'night';
  username: string;
  isoDate: string;
}): React.ReactElement {
  const template = copy.today.greeting[period];
  const greeting = template.replace('{nome}', username);
  return (
    <header className="flex flex-col gap-[var(--spacing-1)]">
      {/* UI-SPEC §3.2 escape hatch — Instrument Serif greeting, max 1/page */}
      <h1
        className="font-[family-name:var(--font-display)] font-medium leading-[var(--leading-tight)] text-[length:var(--text-display-serif)] text-[color:var(--color-text)]"
      >
        {greeting}
      </h1>
      <p className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] capitalize">
        {italianDateLong(new Date(isoDate))}
      </p>
    </header>
  );
}

export default function Today(): React.ReactElement {
  const { data, isLoading, isError } = useToday();
  const complete = useCompleteMeal();
  const username = useAuthStore((s) => s.user?.username) ?? '';

  if (isLoading) {
    return (
      <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-4)] max-w-3xl mx-auto">
        <Skeleton className="h-9 w-2/3" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </main>
    );
  }

  if (isError || !data) {
    // Network failure with no cached fallback — surface italian error inline.
    return (
      <main
        className="p-[var(--spacing-6)] flex flex-col items-center justify-center gap-[var(--spacing-3)] min-h-[60vh] max-w-3xl mx-auto"
        role="alert"
      >
        <p className="text-[color:var(--color-text-muted)] text-center">
          {copy.errors.generic500}
        </p>
      </main>
    );
  }

  if (data.meals.length === 0) {
    // Empty state: no active plan. Tone — minimalist Italian, no `!`.
    return (
      <main className="p-[var(--spacing-6)] flex flex-col items-center justify-center gap-[var(--spacing-4)] min-h-[60vh] max-w-3xl mx-auto">
        <Greeting
          period={data.greeting_period}
          username={username}
          isoDate={data.date}
        />
        <div className="flex flex-col items-center gap-[var(--spacing-2)] mt-[var(--spacing-6)]">
          <h2 className="text-[var(--text-heading)] font-semibold text-[color:var(--color-text)]">
            {copy.today.emptyNoPlan.heading}
          </h2>
          <p className="text-[color:var(--color-text-muted)] text-center">
            {copy.today.emptyNoPlan.body}
          </p>
          <Link
            to="/piano"
            className="text-[color:var(--color-coral-700)] underline underline-offset-4 mt-[var(--spacing-2)] min-h-11 inline-flex items-center"
          >
            {copy.today.emptyNoPlan.cta}
          </Link>
        </div>
        <section className="grid grid-cols-1 md:grid-cols-2 gap-[var(--spacing-4)] w-full mt-[var(--spacing-6)]">
          <WeightQuickLog existing={data.weight_today ?? null} />
          <WorkoutForm existing={data.workout_today ?? null} />
        </section>
        <AIWidget />
      </main>
    );
  }

  return (
    <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-6)] max-w-3xl mx-auto">
      <Greeting
        period={data.greeting_period}
        username={username}
        isoDate={data.date}
      />

      <section
        className="flex flex-col gap-[var(--spacing-3)]"
        aria-label="Pasti di oggi"
      >
        {data.meals.map((m) => (
          <MealCard
            key={`${m.meal_type}-${m.variant_key}`}
            meal={m}
            onToggle={() => complete.mutate(m.meal_type)}
            disabled={complete.isPending}
          />
        ))}
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-[var(--spacing-4)]">
        <WeightQuickLog existing={data.weight_today ?? null} />
        <WorkoutForm existing={data.workout_today ?? null} />
      </section>

      <AIWidget />
    </main>
  );
}
