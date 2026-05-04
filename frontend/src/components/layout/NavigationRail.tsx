// frontend/src/components/layout/NavigationRail.tsx
// UI-SPEC §6.3 — desktop ≥768px navigation rail.
// Plan 01-09 — Phosphor icons via facade; active state leaf-100 bg + leaf-700 text
// (Lifesum signature). Compact 64px-wide rail with 4 destinations.
import { NavLink } from 'react-router';
import {
  CalendarBlank,
  CalendarDots,
  ClockCounterClockwise,
  House,
  UserIcon,
} from '@/components/icons';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';
import type { ComponentType, SVGProps } from 'react';

type IconC = ComponentType<
  { size?: number; weight?: 'regular' | 'fill' | 'bold' } & SVGProps<SVGSVGElement>
>;

interface RailItem {
  to: string;
  label: string;
  Icon: IconC;
}

const ITEMS: RailItem[] = [
  { to: '/today', label: copy.appBar.today, Icon: House as IconC },
  { to: '/settimana', label: copy.appBar.week, Icon: CalendarDots as IconC },
  { to: '/storico', label: copy.appBar.history, Icon: ClockCounterClockwise as IconC },
  { to: '/piano', label: copy.appBar.plan, Icon: CalendarBlank as IconC },
  { to: '/impostazioni', label: copy.appBar.settings, Icon: UserIcon as IconC },
];

export function NavigationRail() {
  return (
    <aside
      className="hidden md:flex flex-col py-[var(--spacing-6)] px-[var(--spacing-2)] gap-[var(--spacing-2)] border-r bg-[var(--color-surface)]"
      style={{
        borderColor: 'var(--color-border)',
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
                ? 'bg-[var(--color-leaf-100)] text-[color:var(--color-leaf-700)]'
                : 'text-[color:var(--color-text-muted)]',
            )
          }
          title={label}
          aria-label={label}
        >
          {({ isActive }) => (
            <Icon size={20} weight={isActive ? 'fill' : 'regular'} aria-hidden="true" />
          )}
        </NavLink>
      ))}
    </aside>
  );
}
