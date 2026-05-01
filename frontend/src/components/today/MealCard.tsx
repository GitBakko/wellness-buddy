// frontend/src/components/today/MealCard.tsx
// UI-SPEC §6.4 — meal card for /today.
//
// Anatomy:
//   meal_type label (italianized) + meal title (h3)
//   MacroDisplay chips (kcal/prot/carbo/grassi)
//   "Segna pasto" / "Pasto registrato" checkbox on the right
//
// Tap target ≥44px on the checkbox label (UI-06).
// All copy from copy.it.ts (FND-09). All colors via @theme tokens (UI-01).

import { Card } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { MacroDisplay } from './MacroDisplay';
import { copy } from '@/i18n/copy.it';
import type { TodayMeal } from '@/services/today';

interface Props {
  meal: TodayMeal;
  onToggle: () => void;
  disabled?: boolean;
}

export function MealCard({ meal, onToggle, disabled }: Props): React.ReactElement {
  const slotLabel = copy.today.mealLabels[meal.meal_type] ?? meal.meal_type;
  const ariaLabel = `${slotLabel}: ${meal.title}`;
  return (
    <Card
      className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-3)]"
      aria-label={ariaLabel}
    >
      <div className="flex items-start justify-between gap-[var(--spacing-3)]">
        <div className="flex flex-col">
          <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] uppercase tracking-wide">
            {slotLabel}
          </span>
          <h3 className="text-[var(--text-base)] font-semibold text-[color:var(--color-text)]">
            {meal.title}
          </h3>
        </div>
        <label className="inline-flex items-center gap-[var(--spacing-2)] min-h-11 cursor-pointer">
          <Checkbox
            checked={meal.completed}
            onCheckedChange={() => {
              if (!meal.completed && !disabled) onToggle();
            }}
            disabled={disabled || meal.completed}
            aria-label={
              meal.completed
                ? copy.today.mealCompletedLabel
                : copy.today.mealMarkCta
            }
          />
          <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)]">
            {meal.completed
              ? copy.today.mealCompletedLabel
              : copy.today.mealMarkCta}
          </span>
        </label>
      </div>
      <MacroDisplay
        kcal={meal.macros.kcal}
        protein_g={meal.macros.protein_g}
        carbs_g={meal.macros.carbs_g}
        fat_g={meal.macros.fat_g}
        variant="compact"
      />
    </Card>
  );
}
