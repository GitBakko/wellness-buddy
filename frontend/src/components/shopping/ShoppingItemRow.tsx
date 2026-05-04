// frontend/src/components/shopping/ShoppingItemRow.tsx
// Plan 02-05 — single row of the shopping list.
//
// UI-SPEC §6.2 anatomy:
//   ┌────────────────────────────────────────────────────────────────────┐
//   │ [☐ Checkbox 24×24 in 44×44 hit area]   Name (--text-base)          │
//   │                                        meal-context caption (opt.) │
//   │                                                       400 g (mono) │
//   └────────────────────────────────────────────────────────────────────┘
//   Checked state: checkbox filled, name + qty strikethrough, opacity 0.5,
//   row background --color-leaf-50 (subtle hint, not a celebration).
//
// All copy from copy.it.ts shopping.* namespace; tokens only.

import * as React from 'react';

import { Checkbox } from '@/components/ui/checkbox';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';
import type { ShoppingItem } from '@/services/shopping';

export interface ShoppingItemRowProps {
  item: ShoppingItem;
  /** Optional meal-context caption (only shown in "Per giorno" view). */
  contextCaption?: string;
  onToggle: (next: boolean) => void;
}

export function ShoppingItemRow({
  item,
  contextCaption,
  onToggle,
}: ShoppingItemRowProps): React.ReactElement {
  const ariaState = item.checked ? copy.shopping.itemCheckedAria : copy.shopping.itemUncheckedAria;
  return (
    <li
      className={cn(
        'flex items-start gap-[var(--spacing-2)] py-[var(--spacing-2)] px-[var(--spacing-3)]',
        'rounded-[var(--radius-sm)]',
        'transition-[background-color,opacity] duration-[var(--duration-fast)] ease-[var(--ease-out-soft)]',
        item.checked && 'bg-[color:var(--color-leaf-50)] opacity-60',
      )}
      data-checked={item.checked ? 'true' : 'false'}
    >
      <Checkbox
        checked={item.checked}
        onCheckedChange={(v) => onToggle(v === true)}
        aria-label={`${item.name_display} — ${ariaState}`}
      />
      <div className="flex-1 min-w-0 mt-[var(--spacing-1)]">
        <div
          className={cn(
            'font-medium text-[length:var(--text-base)] text-[color:var(--color-text)]',
            item.checked && 'line-through',
          )}
        >
          {item.name_display}
        </div>
        {contextCaption ? (
          <div className="text-[length:var(--text-caption)] text-[color:var(--color-text-muted)] uppercase tracking-wide mt-[var(--spacing-1)]">
            {contextCaption}
          </div>
        ) : null}
      </div>
      {item.quantity_it ? (
        <div
          className={cn(
            'shrink-0 self-center font-mono text-[length:var(--text-base)] text-[color:var(--color-text-muted)] tabular-nums',
            item.checked && 'line-through',
          )}
        >
          {item.quantity_it}
        </div>
      ) : null}
    </li>
  );
}
