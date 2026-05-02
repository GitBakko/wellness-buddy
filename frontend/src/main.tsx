// App entry — registers React 19 root with router, query client, sonner toaster.
// Source: 01-RESEARCH.md "Frontend main.tsx entry".
// theme.css MUST be imported before component CSS so tokens cascade.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router';
import { QueryClientProvider } from '@tanstack/react-query';
// Fonts — Plan 01-09 Lifesum Pure migration:
//   Plus Jakarta Sans (variable) is the primary --font-sans (replaces Geist Sans).
//   Geist Mono kept for tabular numerics (macro values, weight, time).
//   Instrument Serif kept for /today greeting display escape hatch (UI-SPEC §3.2).
import '@fontsource-variable/plus-jakarta-sans/index.css';
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
