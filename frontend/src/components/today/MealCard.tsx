// frontend/src/components/today/MealCard.tsx
// Plan 01-09 Lifesum Pure layout — 80×80 photo + info column + 44×44 check button.
//
// Anatomy (mockup A · `.lp-meal`):
//   ┌──────┬──────────────────────────┬────────┐
//   │ 80×  │  CAPTION (uppercase)     │  44×44 │
//   │ 80   │  Title (semibold)        │  ⊙/✓   │
//   │ photo│  P|C|F kcal chip row     │  pill  │
//   └──────┴──────────────────────────┴────────┘
//
// Photo:
//   - When `photo_url` set → <img loading="lazy" width=80 height=80> (DoS mitigation)
//   - When null → gradient placeholder div (leaf-100 → leaf-50) + slot Phosphor icon
//
// Check button (≥44×44 — UI-06 + Plan 07 preserved):
//   - Pending → outline border, neutral icon (Phosphor Circle)
//   - Completed → leaf-500 fill + white Check Phosphor icon
//
// All copy from copy.it.ts; all icons via @/components/icons facade; zero hex.

import { BowlFood, Check, Circle, Cookie, Fish, OrangeSlice } from '@/components/icons';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { copy } from '@/i18n/copy.it';
import { italianNumberInt } from '@/lib/format';
import type { TodayMeal } from '@/services/today';
import type { ComponentType, ReactNode, SVGProps } from 'react';

interface Props {
  meal: TodayMeal;
  onToggle: () => void;
  disabled?: boolean;
  /**
   * Plan 02-02 — optional slot rendered under the macros chip row.
   * Used by /settimana to dock a VariantSelector pill per meal.
   * /today does not pass this prop; legacy callsites unaffected.
   */
  variantSlot?: ReactNode;
  /**
   * Plan 02-05 — when true, the completion check button is omitted entirely.
   * /settimana passes true because completion is owned by /today; rendering a
   * non-functional check button only confused users.
   */
  hideCheckButton?: boolean;
}

type IconC = ComponentType<
  { size?: number; weight?: 'regular' | 'fill' | 'bold' } & SVGProps<SVGSVGElement>
>;

const SLOT_ICON: Record<string, IconC> = {
  breakfast: BowlFood as IconC,
  lunch: BowlFood as IconC,
  dinner: Fish as IconC,
  snack: Cookie as IconC,
};

export function MealCard({
  meal,
  onToggle,
  disabled,
  variantSlot,
  hideCheckButton,
}: Props): React.ReactElement {
  // Plan 02-05 — snack temporal label fallback (when meal.slot is set the
  // user is reading a /settimana snack row or a /today single-snack edge case;
  // /today carousel passes its own slotLabel via the parent header).
  const slotLabel =
    meal.meal_type === 'snack' && meal.slot === 'afternoon'
      ? copy.today.snackLabelAfternoon
      : meal.meal_type === 'snack' && meal.slot === 'evening'
        ? copy.today.snackLabelEvening
        : (copy.today.mealLabels[meal.meal_type] ?? meal.meal_type);
  const ariaLabel = `${slotLabel}: ${meal.title}`;
  const SlotIcon = SLOT_ICON[meal.meal_type] ?? (OrangeSlice as IconC);

  const checkAria = meal.completed
    ? copy.today.mealCompletedLabel
    : copy.today.mealMarkCta;

  return (
    <article
      className="flex items-center gap-[var(--spacing-3)] p-[var(--spacing-3)] bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-md)] shadow-[var(--shadow-1)]"
      aria-label={ariaLabel}
    >
      {/* Photo / placeholder — 80×80 fixed */}
      {meal.photo_url ? (
        <img
          src={meal.photo_url}
          alt=""
          width={80}
          height={80}
          loading="lazy"
          decoding="async"
          className="w-20 h-20 rounded-[var(--radius-sm)] object-cover bg-[var(--color-surface-muted)] flex-shrink-0"
        />
      ) : (
        <div
          aria-hidden="true"
          className="w-20 h-20 rounded-[var(--radius-sm)] flex items-center justify-center flex-shrink-0"
          style={{
            background:
              'linear-gradient(135deg, var(--color-leaf-100), var(--color-leaf-50))',
          }}
        >
          <SlotIcon
            size={28}
            weight="regular"
            aria-hidden="true"
            className="text-[color:var(--color-leaf-700)]"
          />
        </div>
      )}

      {/* Info column */}
      <div className="flex-1 min-w-0 flex flex-col gap-[var(--spacing-1)]">
        <div className="text-[var(--text-caption)] font-bold uppercase tracking-[0.08em] text-[color:var(--color-text-muted)] flex items-center gap-[var(--spacing-1)]">
          {slotLabel}
        </div>
        <h3 className="text-[var(--text-base)] font-semibold leading-tight text-[color:var(--color-text)] m-0 line-clamp-2">
          {meal.title}
        </h3>
        {meal.ingredients && meal.ingredients.length > 0 ? (
          <>
            <ul
              data-testid="meal-ingredients"
              className="flex flex-col gap-[2px] text-[var(--text-caption)] text-[color:var(--color-text-muted)] m-0 p-0 list-none leading-[var(--leading-caption)]"
            >
              {meal.ingredients.slice(0, 5).map((ing, idx) => (
                <li
                  key={`${ing.name}-${idx}`}
                  className="flex items-baseline gap-[var(--spacing-1)] line-clamp-1"
                >
                  <span aria-hidden="true" className="text-[color:var(--color-leaf-500)] font-bold">
                    ·
                  </span>
                  <span className="truncate">
                    {ing.quantity ? `${ing.quantity} ${ing.name}` : ing.name}
                  </span>
                </li>
              ))}
            </ul>
            {meal.ingredients.length > 5 ? (
              <Dialog>
                <DialogTrigger asChild>
                  <button
                    type="button"
                    className="self-start mt-[var(--spacing-1)] text-[var(--text-caption)] font-semibold text-[color:var(--color-leaf-700)] underline-offset-2 hover:underline transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97]"
                  >
                    {copy.today.ingredientsViewAll.replace(
                      '{count}',
                      String(meal.ingredients.length),
                    )}
                  </button>
                </DialogTrigger>
                <DialogContent>
                  <DialogTitle>
                    {copy.today.ingredientsDialogTitle} · {meal.title}
                  </DialogTitle>
                  <ul
                    className="flex flex-col gap-[var(--spacing-1)] mt-[var(--spacing-3)] text-[var(--text-base)] text-[color:var(--color-text)] list-none m-0 p-0 max-h-[60vh] overflow-y-auto"
                  >
                    {meal.ingredients.map((ing, idx) => (
                      <li
                        key={`${ing.name}-full-${idx}`}
                        className="flex items-baseline gap-[var(--spacing-2)] py-[var(--spacing-1)] border-b border-[var(--color-border)] last:border-b-0"
                      >
                        <span
                          aria-hidden="true"
                          className="text-[color:var(--color-leaf-500)] font-bold"
                        >
                          ·
                        </span>
                        <span className="flex-1">
                          {ing.quantity ? `${ing.quantity} ${ing.name}` : ing.name}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <DialogClose asChild>
                    <button
                      type="button"
                      className="mt-[var(--spacing-4)] self-end inline-flex items-center min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)] text-[var(--text-base)] font-semibold transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97]"
                      style={{
                        border: '1.5px solid var(--color-border)',
                        background: 'var(--color-surface)',
                        color: 'var(--color-text)',
                      }}
                    >
                      {copy.today.ingredientsDialogClose}
                    </button>
                  </DialogClose>
                </DialogContent>
              </Dialog>
            ) : null}
          </>
        ) : null}
        <div className="flex flex-wrap gap-[var(--spacing-2)] text-[var(--text-caption)] tabular-nums font-medium text-[color:var(--color-text-muted)]">
          <span
            data-testid="meal-kcal"
            className="font-semibold text-[color:var(--color-text)] whitespace-nowrap"
          >
            {italianNumberInt(meal.macros.kcal)} {copy.today.macroKcal}
          </span>
          <span className="whitespace-nowrap">
            P {italianNumberInt(Math.round(meal.macros.protein_g))} g
          </span>
          <span className="whitespace-nowrap">
            C {italianNumberInt(Math.round(meal.macros.carbs_g))} g
          </span>
          <span className="whitespace-nowrap">
            F {italianNumberInt(Math.round(meal.macros.fat_g))} g
          </span>
        </div>
        {variantSlot ? (
          <div className="mt-[var(--spacing-1)]">{variantSlot}</div>
        ) : null}
      </div>

      {/* Check button — 44×44 minimum. Hidden on /settimana (read-only). */}
      {hideCheckButton ? null : (
        <button
          type="button"
          onClick={() => {
            if (!meal.completed && !disabled) onToggle();
          }}
          disabled={disabled || meal.completed}
          aria-label={checkAria}
          aria-pressed={meal.completed}
          data-completed={meal.completed ? 'true' : undefined}
          className="w-11 h-11 rounded-[var(--radius-pill)] inline-flex items-center justify-center flex-shrink-0 transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97] disabled:cursor-default"
          style={{
            border: meal.completed
              ? '1.5px solid var(--color-leaf-500)'
              : '1.5px solid var(--color-border)',
            background: meal.completed ? 'var(--color-leaf-500)' : 'transparent',
            color: meal.completed
              ? 'var(--color-text-inverse)'
              : 'var(--color-text-muted)',
          }}
        >
          {meal.completed ? (
            <Check size={22} weight="bold" aria-hidden="true" />
          ) : (
            <Circle size={22} weight="regular" aria-hidden="true" />
          )}
        </button>
      )}
    </article>
  );
}
