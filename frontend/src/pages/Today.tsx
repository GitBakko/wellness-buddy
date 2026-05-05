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
import { MealCarousel } from '@/components/today/MealCarousel';
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
 * Plan 02-04 gap-closure — derive macro totals from the today payload.
 *
 * Target precedence:
 *   1. `data.macro_target` (server-resolved from active plan's MACRO TARGET section)
 *   2. Sum of per-meal macros (legacy fallback for plans without macro_target)
 *
 * Consumed = sum across COMPLETED meals only. Using `macro_target` as the ring
 * target prevents the "100% full when 0% consumed" bug that happened when
 * consumed AND target were both 0 → 0/0 → defensive ratio of 1.0.
 */
function aggregateMacros(data: TodayResponse): MacroAggregate {
  let pSum = 0;
  let cSum = 0;
  let fSum = 0;
  let kcalSum = 0;
  let pCurrent = 0;
  let cCurrent = 0;
  let fCurrent = 0;
  let kcalCurrent = 0;
  for (const meal of data.meals) {
    pSum += meal.macros.protein_g;
    cSum += meal.macros.carbs_g;
    fSum += meal.macros.fat_g;
    kcalSum += meal.macros.kcal;
    if (meal.completed) {
      pCurrent += meal.macros.protein_g;
      cCurrent += meal.macros.carbs_g;
      fCurrent += meal.macros.fat_g;
      kcalCurrent += meal.macros.kcal;
    }
  }
  // Prefer server-supplied macro_target; fall back to per-meal sums when absent.
  const target = data.macro_target;
  const kcalTarget = target && target.kcal > 0 ? target.kcal : kcalSum;
  const pTarget = target && target.protein_g > 0 ? target.protein_g : pSum;
  const cTarget = target && target.carbs_g > 0 ? target.carbs_g : cSum;
  const fTarget = target && target.fat_g > 0 ? target.fat_g : fSum;
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

      <MealsSection
        meals={data.meals}
        onToggle={(mt) => complete.mutate(mt)}
        disabled={complete.isPending}
      />


      <section className="grid grid-cols-1 md:grid-cols-2 gap-[var(--spacing-4)]">
        <WeightQuickLog existing={data.weight_today ?? null} />
        <WorkoutForm existing={data.workout_today ?? null} />
      </section>

      <AIWidget />
    </main>
  );
}

// ───────────────────────────────────────────────────────────────────────────
// Plan 02-05 follow-up — group meals so multi-alternative snacks render in
// a swipeable carousel instead of a vertical list of "things to eat together".
// Single-option meals (breakfast / lunch / dinner / single snack) render as
// the existing MealCard. Snacks with the same `slot` (afternoon / evening)
// AND >1 alternatives collapse into one MealCarousel.
// ───────────────────────────────────────────────────────────────────────────
type MealsGroup =
  | { kind: 'single'; meal: import('@/services/today').TodayMeal }
  | {
      kind: 'carousel';
      slot: 'afternoon' | 'evening';
      slotLabel: string;
      options: import('@/services/today').TodayMeal[];
    };

function buildMealGroups(
  meals: import('@/services/today').TodayMeal[],
): MealsGroup[] {
  const groups: MealsGroup[] = [];
  const snackBuckets: Record<string, import('@/services/today').TodayMeal[]> = {
    afternoon: [],
    evening: [],
  };
  // Insertion order preserved so afternoon-snacks render before dinner and
  // evening-snacks after dinner (today_service already orders the array).
  const slotInsertedAt: Record<string, number> = {};

  meals.forEach((m, idx) => {
    if (m.meal_type !== 'snack') {
      groups.push({ kind: 'single', meal: m });
      return;
    }
    const slot: 'afternoon' | 'evening' =
      m.slot === 'evening' ? 'evening' : 'afternoon';
    if (snackBuckets[slot].length === 0) {
      slotInsertedAt[slot] = idx;
      // Reserve a placeholder slot in the groups array; fill after we know
      // how many alternatives this snack-section has.
      groups.push({
        kind: 'carousel',
        slot,
        slotLabel:
          slot === 'evening' ? 'Spuntino serale' : 'Spuntino pomeriggio',
        options: snackBuckets[slot],
      });
    }
    snackBuckets[slot].push(m);
  });

  // Collapse single-alternative snack carousels to plain MealCard so the UI
  // doesn't show a 1-of-1 indicator for spuntini that have no alternatives.
  return groups.flatMap<MealsGroup>((g) => {
    if (g.kind === 'carousel' && g.options.length === 1) {
      return [{ kind: 'single', meal: g.options[0]! }];
    }
    return [g];
  });
}

interface MealsSectionProps {
  meals: import('@/services/today').TodayMeal[];
  onToggle: (mealType: string) => void;
  disabled?: boolean;
}

function MealsSection({ meals, onToggle, disabled }: MealsSectionProps) {
  // Selection happens implicitly: user swipes to the alternative they want
  // and taps the card's check button (one gesture = scelta + segna pasto).
  // No separate "Scegli questa" CTA.
  const groups = buildMealGroups(meals);

  return (
    <section
      className="flex flex-col gap-[var(--spacing-4)]"
      aria-label="Pasti di oggi"
    >
      {groups.map((g, idx) => {
        if (g.kind === 'single') {
          return (
            <MealCard
              key={`${g.meal.meal_type}-${g.meal.variant_key}-${idx}`}
              meal={g.meal}
              onToggle={() => onToggle(g.meal.meal_type)}
              disabled={disabled}
            />
          );
        }
        return (
          <MealCarousel
            key={`carousel-${g.slot}-${idx}`}
            options={g.options}
            slotLabel={g.slotLabel}
            onToggleComplete={onToggle}
            disabled={disabled}
          />
        );
      })}
    </section>
  );
}
