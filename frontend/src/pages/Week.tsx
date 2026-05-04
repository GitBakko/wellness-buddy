// frontend/src/pages/Week.tsx
// Plan 02-02 — /settimana route. WEEK-01..05.
//
// Layout (UI-SPEC §6.3):
//   1. WeekPicker (chip row + jump-to-date popover)
//   2. Hero card: WeeklyMacroRing + DayCompletionStrip
//   3. 7 day sections (sticky day-header + 4 MealCards each with VariantSelector docked)
//
// Cross-user (visibility=group_shared) badges + owner-only logic land Plan 02-06.
// This plan ships the own-user path only (T-API-02).

import * as React from 'react';
import { useNavigate, useParams } from 'react-router';
import { format, parseISO, startOfWeek } from 'date-fns';

import { CalendarBlank } from '@/components/icons';
import { MealCard } from '@/components/today/MealCard';
import { Skeleton } from '@/components/ui/skeleton';
import { DayCompletionStrip } from '@/components/week/DayCompletionStrip';
import { EmptyStateWeek } from '@/components/week/EmptyStateWeek';
import { VariantSelector } from '@/components/week/VariantSelector';
import type { VariantKey } from '@/components/week/VariantSelector';
import { WeekPicker } from '@/components/week/WeekPicker';
import { WeeklyMacroRing } from '@/components/week/WeeklyMacroRing';
import { copy } from '@/i18n/copy.it';
import { italianDateLong } from '@/lib/format';
import { useSetVariant, useWeekly } from '@/services/weekly';
import type { WeeklyMealEntry, WeeklyResponse } from '@/services/weekly';
import { listPlans, type PlanListItem } from '@/services/plans';
import type { TodayMeal } from '@/services/today';
import { useQuery } from '@tanstack/react-query';

/** Returns YYYY-MM-DD for the Monday of the current week (Europe/Rome local clock). */
export function todayStartOfWeek(): string {
  return format(startOfWeek(new Date(), { weekStartsOn: 1 }), 'yyyy-MM-dd');
}

interface WeeklyAggregate {
  kcalConsumed: number;
  kcalTarget: number;
  protein: { current: number; target: number };
  carbs: { current: number; target: number };
  fat: { current: number; target: number };
  completedMeals: number;
  totalMeals: number;
}

function aggregateMacros(data: WeeklyResponse): WeeklyAggregate {
  let kcalT = 0,
    pT = 0,
    cT = 0,
    fT = 0;
  let kcalC = 0,
    pC = 0,
    cC = 0,
    fC = 0;
  let total = 0;
  let done = 0;
  for (const day of data.days) {
    for (const m of day.meals) {
      kcalT += m.macros.kcal ?? 0;
      pT += m.macros.protein_g ?? 0;
      cT += m.macros.carbs_g ?? 0;
      fT += m.macros.fat_g ?? 0;
      total += 1;
      if (m.completed) {
        kcalC += m.macros.kcal ?? 0;
        pC += m.macros.protein_g ?? 0;
        cC += m.macros.carbs_g ?? 0;
        fC += m.macros.fat_g ?? 0;
        done += 1;
      }
    }
  }
  return {
    kcalConsumed: kcalC,
    kcalTarget: kcalT,
    protein: { current: pC, target: pT },
    carbs: { current: cC, target: cT },
    fat: { current: fC, target: fT },
    completedMeals: done,
    totalMeals: total,
  };
}

/** Coerces backend variant_key (Plan 02-02 'A'/'B'/'special'/'pasta'/'default'
 *  OR Plan 02-04 grid keys 'opzione_a'/'opzione_b'/'piatto'/...) → UI VariantKey.
 *
 *  Grid keys are normalized: 'opzione_a' → 'A', 'opzione_b' → 'B', anything
 *  else → 'special'. Subheading-format keys keep their existing mapping.
 */
function toVariantKey(raw: string): VariantKey {
  const low = raw.toLowerCase();
  if (low === 'b' || low === 'opzione_b') return 'B';
  if (
    low === 'special' ||
    low === 'pasta' ||
    low === 'opzione_c' ||
    low === 'opzione_d'
  ) {
    return 'special';
  }
  // Default falls into 'A' bucket — covers 'A', 'opzione_a', 'piatto', 'default',
  // and any unrecognized grid header so the selector lights up the leftmost chip.
  return 'A';
}

/** Inverse of `toVariantKey` — maps a UI VariantKey to the actual backend key
 *  for the given meal's available options. Falls back to the UI key letter when
 *  no option matches (e.g. legacy subheading-format plans where the key is
 *  literally 'A'/'B'/'special').
 */
function fromVariantKey(
  ui: VariantKey,
  options: WeeklyMealEntry['options'],
): string {
  if (!options || options.length === 0) {
    // Subheading-format / legacy — pass UI key through.
    return ui === 'A' ? 'A' : ui === 'B' ? 'B' : 'special';
  }
  // Index-based mapping: A=0, B=1, special=2 (clamped to options.length-1).
  const idx = ui === 'A' ? 0 : ui === 'B' ? 1 : 2;
  const target = options[Math.min(idx, options.length - 1)];
  return target.key;
}

/**
 * Best-effort active plan id. /settimana receives the plan_id only via PATCH payload.
 * We pull it from the /api/plans list (cached via TanStack Query).
 */
function useActivePlanId(): string | null {
  const { data } = useQuery<PlanListItem[]>({
    queryKey: ['plans', 'list'] as const,
    queryFn: listPlans,
    staleTime: 60_000,
  });
  if (!data) return null;
  return data.find((p) => p.is_active)?.id ?? null;
}

/** Map a WeeklyMealEntry to a TodayMeal so MealCard can consume it. */
function toTodayMeal(m: WeeklyMealEntry): TodayMeal {
  return {
    meal_type: m.slot,
    variant_key: m.variant_key,
    title: m.title || '',
    macros: {
      kcal: m.macros.kcal ?? 0,
      protein_g: m.macros.protein_g ?? 0,
      carbs_g: m.macros.carbs_g ?? 0,
      fat_g: m.macros.fat_g ?? 0,
    },
    completed: m.completed,
    photo_url: null,
    // Plan 02-04 gap-closure — surface composition list to MealCard.
    ingredients: m.ingredients ?? [],
  };
}

export default function Week(): React.ReactElement {
  const params = useParams<{ weekStart?: string }>();
  const navigate = useNavigate();
  const weekStart = params.weekStart ?? todayStartOfWeek();

  const { data, isLoading, isError, error } = useWeekly(weekStart);
  const setVariant = useSetVariant(weekStart);
  const planId = useActivePlanId();

  const handleWeekChange = React.useCallback(
    (next: string) => {
      navigate(`/settimana/${next}`);
    },
    [navigate],
  );

  // ── Loading skeleton ───────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-4)] max-w-3xl mx-auto">
        <Skeleton className="h-9 w-2/3" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-56 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </main>
    );
  }

  // ── Error / no plan ────────────────────────────────────────────────────────
  if (isError || !data) {
    // Detect "no_active_plan" via the AUTH-12 envelope and route to the EmptyStateWeek.
    const envelope = (
      error as { response?: { data?: { code?: string } } } | null | undefined
    )?.response?.data;
    if (envelope?.code === 'no_active_plan') {
      return <EmptyStateWeek />;
    }
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

  const macros = aggregateMacros(data);
  const dayCompletions = data.days.map((d) => ({
    dayOfWeek: d.day_of_week,
    completedCount: d.meals.filter((m) => m.completed).length,
    totalCount: d.meals.length,
  }));

  const handleVariantChange = (
    dayOfWeek: number,
    mealType: string,
    nextKey: VariantKey,
    currentUpdatedAt: string | null,
    options: WeeklyMealEntry['options'],
  ) => {
    if (!planId) return;
    // Plan 02-04: translate UI A/B/special back to the actual backend variant_key
    // (grid plans use 'opzione_a'/'opzione_b'/'piatto'; subheading plans use literal 'A'/'B').
    const backendKey = fromVariantKey(nextKey, options);
    setVariant.mutate({
      plan_id: planId,
      day_of_week: dayOfWeek,
      meal_type: mealType,
      variant_key: backendKey,
      ifUnmodifiedSince: currentUpdatedAt,
    });
  };

  return (
    <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-5)] max-w-3xl mx-auto">
      <header className="flex flex-col gap-[var(--spacing-2)]">
        <h1 className="text-[length:var(--text-display)] font-bold leading-[var(--leading-tight)] text-[color:var(--color-text)] m-0">
          {copy.week.heading}
        </h1>
        <WeekPicker value={weekStart} onChange={handleWeekChange} />
      </header>

      {/* Hero card: WeeklyMacroRing + DayCompletionStrip */}
      <section
        className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-card)] p-[var(--spacing-6)] flex flex-col items-center gap-[var(--spacing-5)] shadow-[var(--shadow-2)]"
        aria-label={copy.week.heading}
      >
        <WeeklyMacroRing
          kcalConsumed={macros.kcalConsumed}
          kcalTarget={macros.kcalTarget}
          protein={macros.protein}
          carbs={macros.carbs}
          fat={macros.fat}
          completedMeals={macros.completedMeals}
          totalMeals={macros.totalMeals}
        />
        <DayCompletionStrip days={dayCompletions} />
      </section>

      {/* 7 day sections */}
      <section
        className="flex flex-col gap-[var(--spacing-5)]"
        aria-label="Giorni della settimana"
      >
        {data.days.map((day) => {
          const dayDate = parseISO(day.date);
          const completed = day.meals.filter((m) => m.completed).length;
          const summary = copy.week.daySummaryFormat
            .replace('{count}', String(day.meals.length))
            .replace(
              '{kcal}',
              String(
                day.meals.reduce((acc, m) => acc + (m.macros.kcal ?? 0), 0),
              ),
            );
          return (
            <article
              key={day.date}
              className="flex flex-col gap-[var(--spacing-3)]"
            >
              <header
                className="sticky top-0 z-10 flex items-baseline justify-between gap-[var(--spacing-3)] bg-[var(--color-bg)] py-[var(--spacing-2)]"
              >
                <h2 className="text-[length:var(--text-heading)] font-semibold text-[color:var(--color-text)] m-0 capitalize">
                  {italianDateLong(dayDate)}
                </h2>
                <span className="text-[length:var(--text-caption)] text-[color:var(--color-text-muted)] tabular-nums whitespace-nowrap">
                  {completed}/{day.meals.length} · {summary}
                </span>
              </header>
              <ul className="flex flex-col gap-[var(--spacing-3)] list-none p-0 m-0">
                {day.meals.map((m) => {
                  const todayMeal = toTodayMeal(m);
                  const mealLabel = copy.today.mealLabels[m.slot] ?? m.slot;
                  // Lunch + dinner support 3-variant selector; breakfast/snack do not.
                  const showSelector =
                    m.slot === 'lunch' || m.slot === 'dinner';
                  const variantSlot = showSelector ? (
                    <VariantSelector
                      value={toVariantKey(m.variant_key)}
                      onChange={(next) =>
                        handleVariantChange(
                          day.day_of_week,
                          m.slot,
                          next,
                          m.updated_at,
                          m.options,
                        )
                      }
                      mealLabel={mealLabel}
                      disabled={setVariant.isPending}
                    />
                  ) : null;
                  return (
                    <li key={`${day.date}-${m.slot}`}>
                      <MealCard
                        meal={todayMeal}
                        onToggle={() => {
                          /* /today owns the complete-meal mutation; /settimana is read-only for completion */
                        }}
                        disabled
                        variantSlot={variantSlot}
                      />
                    </li>
                  );
                })}
              </ul>
            </article>
          );
        })}
      </section>

      <footer className="flex items-center justify-center gap-[var(--spacing-2)] text-[color:var(--color-text-muted)] text-[length:var(--text-caption)] py-[var(--spacing-4)]">
        <CalendarBlank size={16} weight="regular" aria-hidden="true" />
        <span>{copy.week.weekPickerCurrentLabel}</span>
      </footer>
    </main>
  );
}
