// frontend/src/pages/Today.tsx
// Phase 1 deliverable — the page the user lands on after login.
//
// UI-SPEC §3.2 — ESCAPE HATCH: this is the ONLY place in src/ permitted to use
//   `--text-display-serif` (Instrument Serif 36px). The greeting <h1> uses it; nothing
//   else may. ESLint hex-ban + grep gate verify.
//
// Plan 01-09 layout (Lifesum Pure mockup A):
//   1. Greeting <h1> (Instrument Serif escape hatch) + date + score pill
//   2. Hero ring card: <MacroRing> + <MacroDisplay> (3-up macro pills)
//   3. Section heading "I tuoi pasti" + completed counter
//   4. Meal list (uses MealCard)
//   5. WeightQuickLog + WorkoutForm (responsive 2-col on md+)
//   6. AIWidget placeholder (locked — no data, no network)

import { Link } from 'react-router';

import { Leaf, UploadSimple } from '@/components/icons';
import { AIWidget } from '@/components/ai/AIWidget';
import { MacroRing } from '@/components/today/MacroRing';
import { MacroDisplay } from '@/components/today/MacroDisplay';
import { MealCard } from '@/components/today/MealCard';
import { WeightQuickLog } from '@/components/today/WeightQuickLog';
import { WorkoutForm } from '@/components/today/WorkoutForm';
import { Skeleton } from '@/components/ui/skeleton';
import { copy } from '@/i18n/copy.it';
import { italianDateLong } from '@/lib/format';
import { useToday, useCompleteMeal } from '@/services/today';
import type { TodayResponse } from '@/services/today';
import { useAuthStore } from '@/stores/auth';

interface MacroAggregate {
  kcalConsumed: number;
  kcalTarget: number;
  protein: { current: number; target: number };
  carbs: { current: number; target: number };
  fat: { current: number; target: number };
}

/**
 * Plan 01-09 — derive macro totals from the today payload meals.
 *
 * Phase 1 simplification: macro_target is derived as the sum of every meal's
 * macros (treating the plan's total daily allowance as "what's planned today").
 * Consumed is the sum across COMPLETED meals only. This is intentionally a
 * thin client-side aggregator; Phase 2 will move totals into TodayResponse
 * once the macro_target sits on `User` / `NutritionPlan` columns.
 */
function aggregateMacros(data: TodayResponse): MacroAggregate {
  let pTarget = 0;
  let cTarget = 0;
  let fTarget = 0;
  let kcalTarget = 0;
  let pCurrent = 0;
  let cCurrent = 0;
  let fCurrent = 0;
  let kcalCurrent = 0;
  for (const meal of data.meals) {
    pTarget += meal.macros.protein_g;
    cTarget += meal.macros.carbs_g;
    fTarget += meal.macros.fat_g;
    kcalTarget += meal.macros.kcal;
    if (meal.completed) {
      pCurrent += meal.macros.protein_g;
      cCurrent += meal.macros.carbs_g;
      fCurrent += meal.macros.fat_g;
      kcalCurrent += meal.macros.kcal;
    }
  }
  return {
    kcalConsumed: kcalCurrent,
    kcalTarget,
    protein: { current: pCurrent, target: pTarget },
    carbs: { current: cCurrent, target: cTarget },
    fat: { current: fCurrent, target: fTarget },
  };
}

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
    <header className="flex items-start justify-between gap-[var(--spacing-3)]">
      <div className="flex flex-col gap-[var(--spacing-1)] min-w-0">
        {/* UI-SPEC §3.2 escape hatch — Instrument Serif greeting, max 1/page */}
        <h1
          className="font-[family-name:var(--font-display)] font-medium leading-[var(--leading-tight)] text-[length:var(--text-display-serif)] text-[color:var(--color-text)] m-0"
        >
          {greeting}
        </h1>
        <p className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] capitalize m-0 font-medium">
          {italianDateLong(new Date(isoDate))}
        </p>
      </div>
      <span
        className="inline-flex items-center gap-[var(--spacing-1)] px-[var(--spacing-3)] py-[var(--spacing-2)] bg-[var(--color-leaf-100)] text-[color:var(--color-leaf-700)] rounded-[var(--radius-pill)] text-[var(--text-caption)] font-semibold flex-shrink-0"
        aria-label={copy.today.scorePillGood}
      >
        <Leaf size={16} weight="fill" aria-hidden="true" />
        <span>{copy.today.scorePillGood}</span>
      </span>
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
        <Skeleton className="h-56 w-full" />
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
        <div className="flex flex-col items-center gap-[var(--spacing-3)] mt-[var(--spacing-6)] text-center">
          <h2 className="text-[var(--text-heading)] font-semibold text-[color:var(--color-text)]">
            {copy.today.emptyNoPlan.heading}
          </h2>
          <p className="text-[color:var(--color-text-muted)] max-w-[30ch]">
            {copy.today.emptyNoPlan.body}
          </p>
          <Link
            to="/piano"
            className="inline-flex items-center gap-[var(--spacing-2)] px-[var(--spacing-6)] py-[var(--spacing-3)] mt-[var(--spacing-2)] bg-[var(--color-leaf-500)] text-[color:var(--color-text-inverse)] rounded-[var(--radius-pill)] font-bold min-h-12 shadow-[var(--shadow-1)]"
          >
            <UploadSimple size={18} weight="fill" aria-hidden="true" />
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

  const macros = aggregateMacros(data);
  const completedCount = data.meals.filter((m) => m.completed).length;
  const sectionMeta = copy.today.sectionMealsCount
    .replace('{done}', String(completedCount))
    .replace('{total}', String(data.meals.length));

  return (
    <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-5)] max-w-3xl mx-auto">
      <Greeting
        period={data.greeting_period}
        username={username}
        isoDate={data.date}
      />

      {/* Hero: macro ring + 3-up macro pills */}
      <section
        className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-card)] p-[var(--spacing-6)] flex flex-col items-center gap-[var(--spacing-5)] shadow-[var(--shadow-2)]"
        aria-label="Riepilogo macro di oggi"
      >
        <MacroRing
          kcalConsumed={macros.kcalConsumed}
          kcalTarget={macros.kcalTarget}
          protein={macros.protein}
          carbs={macros.carbs}
          fat={macros.fat}
        />
        <MacroDisplay
          protein={macros.protein}
          carbs={macros.carbs}
          fat={macros.fat}
        />
      </section>

      {/* Section heading */}
      <div className="flex items-baseline justify-between">
        <h2 className="text-[var(--text-heading)] font-semibold text-[color:var(--color-text)] m-0">
          {copy.today.sectionMeals}
        </h2>
        <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] font-medium tabular-nums">
          {sectionMeta}
        </span>
      </div>

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
