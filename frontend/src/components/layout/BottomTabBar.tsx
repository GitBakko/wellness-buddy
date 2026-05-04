// frontend/src/components/layout/BottomTabBar.tsx
// UI-SPEC §6.3 — mobile bottom tab bar (4 tabs Oggi/Storico/Piano/Impostazioni).
// Plan 01-09 — switched from lucide-react to Phosphor via the icon facade.
//   Active tab: leaf-700 + filled icon weight (Lifesum signature).
//   Inactive: text-muted + regular weight.
//   Hit target ≥ 44×44 (UI-13). Hidden ≥768px in favor of NavigationRail.
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

interface Tab {
  to: string;
  label: string;
  Icon: IconC;
}

const TABS: Tab[] = [
  { to: '/today', label: copy.appBar.today, Icon: House as IconC },
  { to: '/settimana', label: copy.appBar.week, Icon: CalendarDots as IconC },
  { to: '/storico', label: copy.appBar.history, Icon: ClockCounterClockwise as IconC },
  { to: '/piano', label: copy.appBar.plan, Icon: CalendarBlank as IconC },
  { to: '/impostazioni', label: copy.appBar.settings, Icon: UserIcon as IconC },
];

export function BottomTabBar() {
  return (
    <nav
      className="md:hidden sticky bottom-0 z-30 flex items-center justify-around px-[var(--spacing-2)] safe-bottom"
      style={{
        height: 'calc(56px + env(safe-area-inset-bottom))',
        background: 'var(--color-surface)',
        borderTop: '1px solid var(--color-border)',
      }}
      aria-label="Navigazione principale"
    >
      {TABS.map(({ to, label, Icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            cn(
              'flex flex-col items-center gap-1 min-w-11 min-h-11 justify-center font-semibold',
              isActive
                ? 'text-[color:var(--color-leaf-700)]'
                : 'text-[color:var(--color-text-muted)]',
            )
          }
        >
          {({ isActive }) => (
            <>
              <Icon
                size={22}
                weight={isActive ? 'fill' : 'regular'}
                aria-hidden="true"
              />
              <span className="text-[var(--text-caption)]">{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
