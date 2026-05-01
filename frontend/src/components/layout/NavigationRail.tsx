// frontend/src/components/layout/NavigationRail.tsx
// UI-SPEC §6.3 — desktop ≥768px navigation rail.
// Phase 1 ships compact 64px-wide rail with 4 destinations.
// Plan 08+ may extend to collapsible 64/224 with labels.
import { NavLink } from 'react-router';
import { Home, History, FileText, Settings } from 'lucide-react';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';

const ITEMS = [
  { to: '/today', label: copy.appBar.today, Icon: Home },
  { to: '/storico', label: copy.appBar.history, Icon: History },
  { to: '/piano', label: copy.appBar.plan, Icon: FileText },
  { to: '/impostazioni', label: copy.appBar.settings, Icon: Settings },
];

export function NavigationRail() {
  return (
    <aside
      className="hidden md:flex flex-col py-[var(--spacing-6)] px-[var(--spacing-2)] gap-[var(--spacing-2)] border-r"
      style={{
        borderColor: 'var(--color-neutral-200)',
        minWidth: 64,
        width: 64,
      }}
      aria-label="Navigazione laterale"
    >
      {ITEMS.map(({ to, label, Icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            cn(
              'flex items-center justify-center w-11 h-11 rounded-[var(--radius-md)] mx-auto',
              isActive
                ? 'bg-[var(--color-surface-muted)] text-[var(--color-coral-500)]'
                : 'text-[var(--color-neutral-500)]',
            )
          }
          title={label}
          aria-label={label}
        >
          <Icon size={20} strokeWidth={1.75} aria-hidden="true" />
        </NavLink>
      ))}
    </aside>
  );
}
