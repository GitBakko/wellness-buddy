// frontend/src/components/week/EmptyStateWeek.tsx
// Plan 02-02 — empty state for /settimana when no active plan exists.
//
// UI-SPEC §6.2 anatomy:
//   - Phosphor CalendarBlank illustration 240×240 (mobile) / 280×280 (desktop)
//     leaf-200 fill (decorative, aria-hidden)
//   - Heading from copy.week.emptyHeading (--text-heading semibold)
//   - Body from copy.week.emptyBody (--color-text-muted)
//   - CTA leaf-500 button → useNavigate('/piano') with copy.week.emptyCta
//
// All copy from copy.it.ts week.* namespace; all colors via @theme tokens.

import { Link } from 'react-router';

import { CalendarBlank, UploadSimple } from '@/components/icons';
import { copy } from '@/i18n/copy.it';

export function EmptyStateWeek(): React.ReactElement {
  return (
    <section
      className="flex flex-col items-center justify-center gap-[var(--spacing-4)] min-h-[60vh] p-[var(--spacing-6)] text-center"
      role="status"
    >
      <CalendarBlank
        size={240}
        weight="duotone"
        aria-hidden="true"
        className="text-[color:var(--color-leaf-200)] md:w-[280px] md:h-[280px]"
      />
      <h2 className="text-[length:var(--text-heading)] font-semibold text-[color:var(--color-text)] m-0">
        {copy.week.emptyHeading}
      </h2>
      <p className="text-[color:var(--color-text-muted)] max-w-[34ch] m-0">
        {copy.week.emptyBody}
      </p>
      <Link
        to="/piano"
        className="inline-flex items-center gap-[var(--spacing-2)] px-[var(--spacing-6)] py-[var(--spacing-3)] mt-[var(--spacing-2)] bg-[var(--color-leaf-500)] text-[color:var(--color-text-inverse)] rounded-[var(--radius-pill)] font-bold min-h-12 shadow-[var(--shadow-1)]"
      >
        <UploadSimple size={18} weight="fill" aria-hidden="true" />
        {copy.week.emptyCta}
      </Link>
    </section>
  );
}
