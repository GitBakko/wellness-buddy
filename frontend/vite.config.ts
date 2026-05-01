// Vite 7 + React 19 + Tailwind 4 (@theme)
// Source: 01-RESEARCH.md "Frontend Installation" + Pattern 1
// Note: vite-plugin-pwa wiring lands in Plan 06; package is installed here
// as a transitive dependency only.
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // dev only — prod uses IIS reverse proxy
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    target: 'es2022',
    sourcemap: true,
  },
  define: {
    // Build-time injection — Plan 06 wires real git SHA via CI
    __BUILD_HASH__: JSON.stringify(process.env.VITE_BUILD_HASH ?? 'dev'),
  },
});
