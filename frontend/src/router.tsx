// frontend/src/router.tsx
// react-router v7 createBrowserRouter — Plan 06 split:
//   - Auth routes (/login, /register, /welcome) render BARE (no AppShell chrome)
//   - App routes (/today, /piano, /storico, /impostazioni) wrap in AppShell
//     which adds AppBar + BottomTabBar/NavigationRail + ErrorBoundary +
//     UpdatePromptToast + IOSInstallBanner + useDexieResync.
import { createBrowserRouter, redirect } from 'react-router';
import { AppShell } from './components/layout/AppShell';

export const router = createBrowserRouter([
  // Bare auth routes — no AppShell chrome
  {
    path: '/login',
    lazy: async () => ({ Component: (await import('./pages/Login')).default }),
  },
  {
    path: '/register',
    lazy: async () => ({ Component: (await import('./pages/Register')).default }),
  },
  {
    path: '/welcome',
    lazy: async () => ({
      Component: (await import('./components/auth/PersistStorageWelcome'))
        .PersistStorageWelcome,
    }),
  },
  // App routes wrapped in AppShell
  {
    path: '/',
    Component: AppShell,
    children: [
      { index: true, loader: () => redirect('/today') },
      {
        path: 'today',
        lazy: async () => ({ Component: (await import('./pages/Today')).default }),
      },
      {
        // Phase 2 (Plan 02-02) — /settimana with optional explicit weekStart param.
        // /settimana → resolves to today's Monday at runtime via Week.tsx.
        path: 'settimana',
        lazy: async () => ({ Component: (await import('./pages/Week')).default }),
      },
      {
        path: 'settimana/:weekStart',
        lazy: async () => ({ Component: (await import('./pages/Week')).default }),
      },
      {
        path: 'piano',
        lazy: async () => ({ Component: (await import('./pages/Plans')).default }),
      },
      {
        path: 'storico',
        lazy: async () => ({ Component: (await import('./pages/History')).default }),
      },
      {
        path: 'impostazioni',
        lazy: async () => ({ Component: (await import('./pages/Settings')).default }),
      },
    ],
  },
]);
