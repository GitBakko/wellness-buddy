// frontend/src/components/week/VariantSelector.tsx
// Plan 02-02 — variant selector pill + dropdown menu.
//
// UI-SPEC §6.2 anatomy (Lifesum-style, NOT tabs):
//   Trigger pill (--radius-pill, --spacing-2/-3, --text-base semibold) with
//   active variant label + Phosphor CaretDown 16px. Tap → 80ms scale 0.97.
//   Dropdown (Radix DropdownMenu) lists 3 options: Opzione A (leaf-50), Opzione B
//   (surface-muted), Pasta speciale (coral-50). Each menu item has:
//     - 6×6 leaf-500 dot left when active
//     - Variant label center
//     - MacroDisplay-compact macros chip right
//     - Min item height 56px
//     - Phosphor Check 18px right when this is the current selection
//
// All copy from copy.it.ts week.* namespace; all colors via @theme tokens.

import * as React from 'react';
import { CaretDown, Check } from '@/components/icons';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';
import { italianNumberInt } from '@/lib/format';
import type { WeeklyMacros } from '@/services/weekly';

export type VariantKey = 'A' | 'B' | 'special';

export interface VariantSelectorProps {
  value: VariantKey;
  onChange: (next: VariantKey) => void;
  mealLabel: string;
  /** Optional macro previews per variant (compact "kcal · P/C/F"). */
  macroPreviews?: Partial<Record<VariantKey, WeeklyMacros>>;
  ariaLabel?: string;
  disabled?: boolean;
}

const VARIANT_ORDER: VariantKey[] = ['A', 'B', 'special'];

const VARIANT_LABEL: Record<VariantKey, string> = {
  A: copy.week.variantOptionA,
  B: copy.week.variantOptionB,
  special: copy.week.variantSpecial,
};

const VARIANT_BG_VAR: Record<VariantKey, string> = {
  A: '--color-leaf-50',
  B: '--color-surface-muted',
  special: '--color-coral-50',
};

function formatMacroPreview(m: WeeklyMacros | undefined): string | null {
  if (!m) return null;
  return copy.week.variantSelectorMacroFormat
    .replace('{kcal}', italianNumberInt(Math.round(m.kcal)))
    .replace('{protein}', italianNumberInt(Math.round(m.protein_g)))
    .replace('{carbs}', italianNumberInt(Math.round(m.carbs_g)))
    .replace('{fat}', italianNumberInt(Math.round(m.fat_g)));
}

export function VariantSelector({
  value,
  onChange,
  mealLabel,
  macroPreviews,
  ariaLabel,
  disabled = false,
}: VariantSelectorProps): React.ReactElement {
  const triggerLabel = VARIANT_LABEL[value];
  const computedAria =
    ariaLabel ??
    copy.week.variantSelectorAria.replace('{meal}', mealLabel);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label={computedAria}
          disabled={disabled}
          data-variant={value}
          className={cn(
            'inline-flex items-center gap-[var(--spacing-1)]',
            'px-[var(--spacing-3)] py-[var(--spacing-2)]',
            'rounded-[var(--radius-pill)] border border-[var(--color-border)]',
            'text-[length:var(--text-base)] font-semibold',
            'text-[color:var(--color-text)]',
            'min-h-11 min-w-11',
            'transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)]',
            'active:scale-[0.97] disabled:opacity-60 disabled:cursor-not-allowed',
          )}
          style={{
            background: `var(${VARIANT_BG_VAR[value]})`,
          }}
        >
          <span className="truncate">{triggerLabel}</span>
          <CaretDown size={16} weight="bold" aria-hidden="true" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="start"
        className="min-w-[14rem] flex flex-col gap-[var(--spacing-1)] p-[var(--spacing-2)]"
      >
        {VARIANT_ORDER.map((key) => {
          const isActive = key === value;
          const macroPreview = formatMacroPreview(macroPreviews?.[key]);
          return (
            <DropdownMenuItem
              key={key}
              onSelect={(e) => {
                e.preventDefault();
                if (!isActive) onChange(key);
              }}
              data-active={isActive ? 'true' : undefined}
              aria-current={isActive ? 'true' : undefined}
              className={cn(
                'flex items-center gap-[var(--spacing-2)]',
                'px-[var(--spacing-3)] py-[var(--spacing-2)]',
                'rounded-[var(--radius-md)]',
                'text-[length:var(--text-base)]',
                'min-h-14 cursor-pointer',
              )}
              style={{
                background: isActive
                  ? `var(${VARIANT_BG_VAR[key]})`
                  : undefined,
              }}
            >
              {/* Active dot — 6×6 leaf-500 left rail */}
              <span
                aria-hidden="true"
                className={cn(
                  'w-[6px] h-[6px] rounded-[var(--radius-pill)] flex-shrink-0',
                )}
                style={{
                  background: isActive
                    ? 'var(--color-leaf-500)'
                    : 'transparent',
                }}
              />
              <div className="flex-1 min-w-0 flex flex-col gap-[2px]">
                <span className="font-semibold text-[color:var(--color-text)] truncate">
                  {VARIANT_LABEL[key]}
                  {isActive ? (
                    <span className="sr-only">
                      {' '}
                      ({copy.week.variantSelectorActive})
                    </span>
                  ) : null}
                </span>
                {macroPreview ? (
                  <span className="text-[length:var(--text-caption)] text-[color:var(--color-text-muted)] tabular-nums truncate">
                    {macroPreview}
                  </span>
                ) : null}
              </div>
              {isActive ? (
                <Check
                  size={18}
                  weight="bold"
                  aria-hidden="true"
                  className="text-[color:var(--color-leaf-700)] flex-shrink-0"
                />
              ) : null}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
