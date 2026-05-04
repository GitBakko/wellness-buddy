// frontend/src/router.tsx
// react-router v7 createBrowserRouter — Plan 06 split:
//   - Auth routes (/login, /register, /welcome) render BARE (no AppShell chrome)
//   - App routes (/today, /piano, /storico, /impostazioni) wrap in AppShell
//     which adds AppBar + BottomTabBar/NavigationRail + ErrorBoundary +
//     UpdatePromptToast + IOSInstallBanner + useDexieResync.
//
// Plan 02-03 (gap closure): AppShell route now has a loader that hydrates
// the in-memory access token from the HttpOnly refresh cookie BEFORE
// children render. Without this, page refresh on /today/etc. left the
// store with accessToken=null, queries 401-d, and the ErrorBoundary
// caught a generic "Qualcosa non ha funzionato".
import { createBrowserRouter, redirect } from 'react-router';
import { AppShell } from './components/layout/AppShell';
import { useAuthStore } from './stores/auth';
import { refreshTokenAtomic } from './lib/refreshTokenAtomic';

async function appShellLoader() {
  const state = useAuthStore.getState();

  // If we already have an access token + user, no hydration needed.
  if (state.accessToken && state.user) return null;

  // Try to silently refresh from the HttpOnly cookie.
  try {
    if (!state.accessToken) {
      await refreshTokenAtomic();
    }
  } catch {
    // refreshTokenAtomic clears the store on failure
    return redirect('/login');
  }

  // Re-read store; refreshTokenAtomic populated accessToken
  const access = useAuthStore.getState().accessToken;
  if (!access) return redirect('/login');

  // Fetch user profile if missing (only on cold boot; subsequent navigation
  // hits this branch never because state.user persists in memory).
  if (!useAuthStore.getState().user) {
    try {
      const res = await fetch('/api/auth/me', {
        method: 'GET',
        credentials: 'include',
        headers: {
          Authorization: `Bearer ${access}`,
          Accept: 'application/json',
        },
      });
      if (!res.ok) {
        useAuthStore.getState().clear();
        return redirect('/login');
      }
      const user = await res.json();
      useAuthStore.getState().setUser(user);
    } catch {
      useAuthStore.getState().clear();
      return redirect('/login');
    }
  }

  return null;
}

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
    loader: appShellLoader,
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
