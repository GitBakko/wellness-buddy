// frontend/src/test/setup.ts
// Vitest setup — runs once per test file before tests.
//
// Responsibilities:
//   1. Register @testing-library/jest-dom matchers (`toBeInTheDocument`, etc.)
//   2. Mock window.matchMedia (jsdom doesn't ship it; useReducedMotion/useMediaQuery break otherwise)
//   3. Inject Tailwind 4 motion tokens as a `<style>` tag so motion.test.ts can read
//      `--motion-scale` via getComputedStyle. Mirror of theme.css §Motion + reduce media query.

import '@testing-library/jest-dom/vitest';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(() => {
  cleanup();
});

// ── matchMedia mock ─────────────────────────────────────────────────────────────
// jsdom lacks matchMedia. Tests that exercise prefers-reduced-motion override
// `window.matchMedia` per-test (motion.test.ts does this).
if (typeof window !== 'undefined' && !window.matchMedia) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated, but referenced by some libs
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

// ── Theme tokens (motion budget) injected for getComputedStyle reads ────────────
// Mirror of Plan 05a's theme.css §Motion + prefers-reduced-motion media query.
// Kept narrow — only motion tokens needed by motion.test.ts. Adding more tokens
// here is safe but increases test runtime; stick to the minimum.
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.id = 'wb-test-theme-tokens';
  style.textContent = `
    :root {
      --duration-instant: 80ms;
      --duration-fast: 150ms;
      --duration-base: 250ms;
      --duration-slow: 400ms;
      --duration-celebration: 800ms;
      --motion-scale: 1;
    }
    @media (prefers-reduced-motion: reduce) {
      :root { --motion-scale: 0; }
      *, *::before, *::after {
        animation-duration: 0ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0ms !important;
        scroll-behavior: auto !important;
      }
    }
  `;
  document.head.appendChild(style);
}
