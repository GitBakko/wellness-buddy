// frontend/src/components/layout/AppBar.tsx
// UI-SPEC §6.3 — sticky top bar, height 56px + safe-area, backdrop-blur,
// dynamic title from current route, SyncStatusPip on right.
import { useLocation } from 'react-router';
import { copy } from '@/i18n/copy.it';
import { SyncStatusPip } from './SyncStatusPip';

const TITLE_BY_PATH: Record<string, string> = {
  '/today': copy.appBar.today,
  '/storico': copy.appBar.history,
  '/piano': copy.appBar.plan,
  '/impostazioni': copy.appBar.settings,
};

export function AppBar() {
  const { pathname } = useLocation();
  const title = TITLE_BY_PATH[pathname] ?? 'Wellness Buddy';
  return (
    <header
      className="sticky top-0 z-30 flex items-center px-[var(--spacing-4)] safe-top"
      style={{
        height: 'calc(56px + env(safe-area-inset-top))',
        background: 'color-mix(in oklch, var(--color-bg) 85%, transparent)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        borderBottom: '1px solid var(--color-neutral-200)',
      }}
    >
      <h1 className="text-[var(--text-base)] font-[600]">{title}</h1>
      <div className="ml-auto flex items-center gap-[var(--spacing-3)]">
        <SyncStatusPip />
      </div>
    </header>
  );
}
