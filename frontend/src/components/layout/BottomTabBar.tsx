// frontend/src/components/layout/BottomTabBar.tsx
// UI-SPEC §6.3 — mobile bottom tab bar (4 tabs Oggi/Storico/Piano/Impostazioni).
// Hit target ≥ 44×44 (UI-13). Active tab uses --color-coral-500 accent.
// Hidden ≥768px in favor of NavigationRail.
import { NavLink } from 'react-router';
import { Home, History, FileText, Settings } from 'lucide-react';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';

const TABS = [
  { to: '/today', label: copy.appBar.today, Icon: Home },
  { to: '/storico', label: copy.appBar.history, Icon: History },
  { to: '/piano', label: copy.appBar.plan, Icon: FileText },
  { to: '/impostazioni', label: copy.appBar.settings, Icon: Settings },
];

export function BottomTabBar() {
  return (
    <nav
      className="md:hidden sticky bottom-0 z-30 flex items-center justify-around px-[var(--spacing-2)] safe-bottom"
      style={{
        height: 'calc(56px + env(safe-area-inset-bottom))',
        background: 'var(--color-bg)',
        borderTop: '1px solid var(--color-neutral-200)',
      }}
      aria-label="Navigazione principale"
    >
      {TABS.map(({ to, label, Icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            cn(
              'flex flex-col items-center gap-1 min-w-11 min-h-11 justify-center',
              isActive
                ? 'text-[var(--color-coral-500)]'
                : 'text-[var(--color-neutral-500)]',
            )
          }
        >
          <Icon size={24} strokeWidth={1.75} aria-hidden="true" />
          <span className="text-[var(--text-caption)]">{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
