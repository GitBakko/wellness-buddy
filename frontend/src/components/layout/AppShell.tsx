// frontend/src/components/layout/AppShell.tsx
// UI-SPEC §6.3 — full app shell composition for protected routes.
//
// Layout (mobile-first):
//   ┌───────────────────────────────┐
//   │         AppBar (sticky)       │  ← title + SyncStatusPip
//   ├───────────────────────────────┤
//   │                               │
//   │      <Outlet />               │  ← page content (Today/Plans/...)
//   │                               │
//   ├───────────────────────────────┤
//   │     BottomTabBar (mobile)     │  ← 4 tabs
//   └───────────────────────────────┘
//
// Desktop ≥768px adds NavigationRail on the left and hides BottomTabBar.
//
// Cross-cutting: ErrorBoundary wraps everything, UpdatePromptToast mounts
// version polling, IOSInstallBanner conditionally appears on 2nd-visit iOS.
// useDexieResync runs on mount to recover from iOS storage eviction.
import { Outlet } from 'react-router';
import { AppBar } from './AppBar';
import { BottomTabBar } from './BottomTabBar';
import { NavigationRail } from './NavigationRail';
import { ErrorBoundary } from './ErrorBoundary';
import { UpdatePromptToast } from './UpdatePromptToast';
import { IOSInstallBanner } from './IOSInstallBanner';
import { useDexieResync } from '@/hooks/useStoragePersist';

export function AppShell() {
  useDexieResync();
  return (
    <ErrorBoundary>
      <UpdatePromptToast />
      <IOSInstallBanner />
      <div className="flex flex-row min-h-dvh">
        <NavigationRail />
        <div className="flex-1 flex flex-col">
          <AppBar />
          <main className="flex-1">
            <Outlet />
          </main>
          <BottomTabBar />
        </div>
      </div>
    </ErrorBoundary>
  );
}
