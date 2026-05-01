// App entry — registers React 19 root with router, query client, sonner toaster.
// Source: 01-RESEARCH.md "Frontend main.tsx entry".
// theme.css MUST be imported before component CSS so tokens cascade.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router';
import { QueryClientProvider } from '@tanstack/react-query';
// Fonts — variable Geist (replaces deprecated `geist` npm pkg which is Next-only)
// and Instrument Serif (regular 400) for the /today greeting escape hatch.
import '@fontsource-variable/geist/index.css';
import '@fontsource-variable/geist-mono/index.css';
import '@fontsource/instrument-serif/400.css';
import './styles/theme.css';
import './styles/globals.css';
import { router } from './router';
import { queryClient } from './lib/queryClient';
import { Toaster } from './components/ui/sonner';

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('Root element #root not found in index.html');

createRoot(rootEl).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster />
    </QueryClientProvider>
  </StrictMode>,
);
