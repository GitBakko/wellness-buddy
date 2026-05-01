// frontend/vitest.config.ts
// Vitest unit-test config (jsdom environment).
//
// Why jsdom:
//   - matchMedia, navigator.onLine, localStorage all polyfilled out of the box
//   - useReducedMotion + useTheme + useOnline hooks need a DOM-ish environment to test
//
// Setup file (`src/test/setup.ts`) injects Tailwind 4 token CSS so tests can read
// `--motion-scale` etc. via getComputedStyle, and registers @testing-library/jest-dom
// matchers like `toBeInTheDocument()`.

import { defineConfig } from 'vitest/config';
import path from 'node:path';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    css: true,
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    // Exclude Playwright e2e and visual specs — those are handled by `playwright test`.
    exclude: ['tests/**', 'node_modules/**', 'dist/**'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
