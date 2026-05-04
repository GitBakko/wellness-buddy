// frontend/src/components/shopping/ShoppingViewToggle.tsx
// Plan 02-05 — segmented control: "Per categoria" / "Per giorno".
//
// 2-button segmented control. Active button shows --color-leaf-100 fill.
// Hit target ≥44px each. Italian-only labels via copy.it.ts.

import * as React from 'react';

import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';

export type ShoppingView = 'category' | 'day';

export interface ShoppingViewToggleProps {
  value: ShoppingView;
  onChange: (next: ShoppingView) => void;
}

export function ShoppingViewToggle({
  value,
  onChange,
}: ShoppingViewToggleProps): React.ReactElement {
  return (
    <div
      role="group"
      aria-label={copy.shopping.viewToggleAriaLabel}
      className={cn(
        'inline-flex p-[var(--spacing-1)] gap-[var(--spacing-1)]',
        'rounded-[var(--radius-pill)] bg-[color:var(--color-surface-muted)]',
        'border border-[color:var(--color-border)]',
      )}
    >
      <button
        type="button"
        onClick={() => onChange('category')}
        aria-pressed={value === 'category'}
        data-active={value === 'category' ? 'true' : undefined}
        className={cn(
          'min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)]',
          'font-medium text-[length:var(--text-base)]',
          'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out-soft)]',
          'active:scale-[calc(1-0.03*var(--motion-scale))]',
          value === 'category'
            ? 'bg-[color:var(--color-leaf-100)] text-[color:var(--color-leaf-700)]'
            : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text)]',
        )}
      >
        {copy.shopping.viewByCategory}
      </button>
      <button
        type="button"
        onClick={() => onChange('day')}
        aria-pressed={value === 'day'}
        data-active={value === 'day' ? 'true' : undefined}
        className={cn(
          'min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)]',
          'font-medium text-[length:var(--text-base)]',
          'transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-out-soft)]',
          'active:scale-[calc(1-0.03*var(--motion-scale))]',
          value === 'day'
            ? 'bg-[color:var(--color-leaf-100)] text-[color:var(--color-leaf-700)]'
            : 'text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text)]',
        )}
      >
        {copy.shopping.viewByDay}
      </button>
    </div>
  );
}
