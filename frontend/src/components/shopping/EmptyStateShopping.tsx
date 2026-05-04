// frontend/src/components/shopping/EmptyStateShopping.tsx
// Plan 02-05 — empty state for /spesa when no active plan exists OR all
// categories are empty (e.g. all variants chosen but no parsed ingredients).
//
// UI-SPEC §6.2 anatomy:
//   - Phosphor ShoppingCart 200×200 (mobile) / 240×240 (desktop) leaf-200,
//     decorative aria-hidden
//   - Heading from copy.shopping.emptyHeading (--text-heading semibold)
//   - Body from copy.shopping.emptyBody (--color-text-muted)
//   - CTA leaf-500 button → /settimana with copy.shopping.emptyCta
//
// All copy from copy.it.ts shopping.* namespace; all colors via @theme tokens.

import * as React from 'react';
import { Link } from 'react-router';

import { ShoppingCart } from '@/components/icons';
import { copy } from '@/i18n/copy.it';

export function EmptyStateShopping(): React.ReactElement {
  return (
    <section
      className="flex flex-col items-center justify-center gap-[var(--spacing-4)] min-h-[60vh] p-[var(--spacing-6)] text-center"
      role="status"
    >
      <ShoppingCart
        size={200}
        weight="duotone"
        aria-hidden="true"
        className="text-[color:var(--color-leaf-200)] md:w-[240px] md:h-[240px]"
      />
      <h2 className="text-[length:var(--text-heading)] font-semibold text-[color:var(--color-text)] m-0">
        {copy.shopping.emptyHeading}
      </h2>
      <p className="text-[color:var(--color-text-muted)] max-w-[34ch] m-0">
        {copy.shopping.emptyBody}
      </p>
      <Link
        to="/settimana"
        className="inline-flex items-center gap-[var(--spacing-2)] px-[var(--spacing-6)] py-[var(--spacing-3)] mt-[var(--spacing-2)] bg-[color:var(--color-leaf-500)] text-[color:var(--color-text-inverse)] rounded-[var(--radius-pill)] font-bold min-h-12 shadow-[var(--shadow-1)]"
      >
        {copy.shopping.emptyCta}
      </Link>
    </section>
  );
}
