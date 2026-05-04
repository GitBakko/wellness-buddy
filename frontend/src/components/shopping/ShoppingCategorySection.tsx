// frontend/src/components/shopping/ShoppingCategorySection.tsx
// Plan 02-05 — collapsible category block.
//
// UI-SPEC §6.2 anatomy:
//   ┌─────────────────────────────────────────────────────────────┐
//   │ [Phosphor icon 22×22] CategoryName (heading)  (count)  ⌄    │  ← 44px header
//   ├─────────────────────────────────────────────────────────────┤
//   │   ShoppingItemRow                                            │
//   │   ShoppingItemRow                                            │
//   │   ...                                                        │
//   └─────────────────────────────────────────────────────────────┘
//
// Phosphor icon by category — Snowflake / Carrot / Package / BowlSteam / Pill.
// Native <details><summary> for the collapse — zero JS, full a11y for free,
// keyboard support inherited from browsers.

import * as React from 'react';

import {
  BowlSteam,
  CaretDown,
  Carrot,
  Package,
  Pill,
  Snowflake,
} from '@/components/icons';
import { ShoppingItemRow } from '@/components/shopping/ShoppingItemRow';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';
import type { ShoppingItem } from '@/services/shopping';

type IconC = React.ComponentType<{
  size?: number;
  weight?: 'regular' | 'fill' | 'bold' | 'duotone';
  className?: string;
  'aria-hidden'?: boolean | 'true' | 'false';
}>;

const CATEGORY_ICON: Record<string, IconC> = {
  'Frigo & Freschi': Snowflake as IconC,
  'Frutta & Verdura': Carrot as IconC,
  Dispensa: Package as IconC,
  Condimenti: BowlSteam as IconC,
  Integratori: Pill as IconC,
};

export interface ShoppingCategorySectionProps {
  name: string;
  items: ShoppingItem[];
  /** Optional caption-builder for the per-day view (returns label per item). */
  itemCaption?: (item: ShoppingItem) => string | undefined;
  defaultOpen?: boolean;
  onToggleItem: (item: ShoppingItem, next: boolean) => void;
}

export function ShoppingCategorySection({
  name,
  items,
  itemCaption,
  defaultOpen = true,
  onToggleItem,
}: ShoppingCategorySectionProps): React.ReactElement {
  const Icon: IconC = CATEGORY_ICON[name] ?? (Package as IconC);
  const total = items.length;
  const checked = items.filter((it) => it.checked).length;
  return (
    <details
      className={cn(
        'group rounded-[var(--radius-card)]',
        'border border-[color:var(--color-border)]',
        'bg-[color:var(--color-surface)]',
      )}
      open={defaultOpen}
      data-category={name}
    >
      <summary
        className={cn(
          'list-none cursor-pointer select-none',
          'flex items-center gap-[var(--spacing-3)]',
          'min-h-11 px-[var(--spacing-4)] py-[var(--spacing-3)]',
          'rounded-[var(--radius-card)]',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--color-focus-ring)]',
        )}
      >
        <Icon
          size={22}
          weight="duotone"
          aria-hidden="true"
          className="text-[color:var(--color-leaf-600)]"
        />
        <h3 className="flex-1 m-0 font-semibold text-[length:var(--text-base)] text-[color:var(--color-text)]">
          {name}
        </h3>
        <span
          className="font-mono text-[length:var(--text-caption)] text-[color:var(--color-text-muted)] tabular-nums"
          aria-label={`${checked} di ${total}`}
        >
          {checked}/{total}
        </span>
        <CaretDown
          size={16}
          weight="bold"
          aria-hidden="true"
          className="text-[color:var(--color-text-muted)] transition-transform duration-[var(--duration-fast)] group-open:rotate-180"
        />
      </summary>
      <div className="px-[var(--spacing-2)] pb-[var(--spacing-2)]">
        {items.length === 0 ? (
          <p className="text-[color:var(--color-text-muted)] px-[var(--spacing-3)] py-[var(--spacing-2)] m-0">
            {copy.shopping.categoryEmpty}
          </p>
        ) : (
          <ul className="list-none p-0 m-0 flex flex-col gap-[var(--spacing-1)]">
            {items.map((it) => (
              <ShoppingItemRow
                key={`${it.canonical_name}-${it.unit ?? 'none'}`}
                item={it}
                contextCaption={itemCaption?.(it)}
                onToggle={(next) => onToggleItem(it, next)}
              />
            ))}
          </ul>
        )}
      </div>
    </details>
  );
}
