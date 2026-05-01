// Router — react-router v7 createBrowserRouter with lazy routes.
// Page modules are placeholders; Plans 03/04/06/07 ship real pages.
import { createBrowserRouter, redirect } from 'react-router';
import App from './App';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, loader: () => redirect('/today') },
      {
        path: 'login',
        lazy: async () => ({ Component: (await import('./pages/Login')).default }),
      },
      {
        path: 'register',
        lazy: async () => ({ Component: (await import('./pages/Register')).default }),
      },
      {
        path: 'welcome',
        lazy: async () => ({
          Component: (await import('./components/auth/PersistStorageWelcome'))
            .PersistStorageWelcome,
        }),
      },
      {
        path: 'today',
        lazy: async () => ({ Component: (await import('./pages/Today')).default }),
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
