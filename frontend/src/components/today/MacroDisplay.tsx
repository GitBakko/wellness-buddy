// frontend/src/components/today/MacroDisplay.tsx
// UI-SPEC §6.4 — macro chips for MealCard. Compact pills with tabular-nums + Italian
// number formatting. Token-only colors (UI-01 + UI-08).

import { italianNumber, italianNumberInt } from '@/lib/format';
import { copy } from '@/i18n/copy.it';

interface Props {
  kcal: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  variant?: 'compact' | 'expanded';
}

export function MacroDisplay({
  kcal,
  protein_g,
  carbs_g,
  fat_g,
  variant = 'compact',
}: Props): React.ReactElement | null {
  if (variant !== 'compact') {
    // Phase 1: only compact in use; expanded reserved for Phase 3 dashboard.
    return null;
  }

  const chip =
    'inline-flex items-center px-[var(--spacing-2)] py-[var(--spacing-1)] ' +
    'rounded-[var(--radius-pill)] bg-[var(--color-surface-muted)] ' +
    'text-[color:var(--color-text)] text-[var(--text-caption)] font-mono tabular-nums';

  return (
    <div
      className="flex flex-wrap gap-[var(--spacing-2)]"
      aria-label="Macronutrienti"
    >
      <span className={chip}>
        {italianNumberInt(kcal)} {copy.today.macroKcal}
      </span>
      <span className={chip}>
        {italianNumber(protein_g)} {copy.today.macroProtChip}
      </span>
      <span className={chip}>
        {italianNumber(carbs_g)} {copy.today.macroCarbChip}
      </span>
      <span className={chip}>
        {italianNumber(fat_g)} {copy.today.macroFat}
      </span>
    </div>
  );
}
