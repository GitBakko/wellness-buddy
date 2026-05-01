// Vite 7 + React 19 + Tailwind 4 (@theme) + vite-plugin-pwa Workbox SW.
// Source: 01-RESEARCH.md Pattern 3 (vite-plugin-pwa) + 01-UI-SPEC.md §10.4 (manifest).
// PITFALLS #2 mitigation: NetworkFirst index.html with 3s timeout.
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'node:path';
import { execSync } from 'node:child_process';

const buildHash = (() => {
  try {
    return execSync('git rev-parse --short HEAD').toString().trim();
  } catch {
    return process.env.VITE_BUILD_HASH ?? 'dev';
  }
})();

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'prompt',
      strategies: 'generateSW',
      injectRegister: 'auto',
      manifest: {
        name: 'Wellness Buddy',
        short_name: 'Wellness',
        description: 'Tracking nutrizionale e wellness',
        lang: 'it',
        start_url: '/today',
        scope: '/',
        display: 'standalone',
        orientation: 'portrait',
        theme_color: '#FAF9F6',
        background_color: '#FAF9F6',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          {
            src: '/icons/icon-maskable-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,woff2,svg,png,webmanifest}'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/version\.json$/],
        cleanupOutdatedCaches: true,
        skipWaiting: false,
        clientsClaim: false,
        runtimeCaching: [
          // PITFALL #2 — NetworkFirst index.html / nav requests with 3s timeout
          {
            urlPattern: ({ request }) => request.mode === 'navigate',
            handler: 'NetworkFirst',
            options: {
              cacheName: 'app-shell',
              networkTimeoutSeconds: 3,
              expiration: { maxEntries: 10, maxAgeSeconds: 7 * 24 * 3600 },
            },
          },
          // CacheFirst hashed assets (immutable filenames → safe long expiry)
          {
            urlPattern: /\/assets\/.*\.(js|css|woff2)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'static-assets',
              expiration: { maxEntries: 100, maxAgeSeconds: 365 * 24 * 3600 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          // Icons + illustrations
          {
            urlPattern: /\/(icons|illustrations)\/.*\.(svg|png)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'static-images',
              expiration: { maxEntries: 50, maxAgeSeconds: 30 * 24 * 3600 },
            },
          },
          // Read API — NetworkFirst with 3s timeout
          {
            urlPattern: /\/api\/(plans|weekly|today|dashboard)\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-reads',
              networkTimeoutSeconds: 3,
              expiration: { maxEntries: 50, maxAgeSeconds: 24 * 3600 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          // Auth — NetworkOnly (never cached)
          { urlPattern: /\/api\/auth\/.*$/, handler: 'NetworkOnly' },
          // Writes — NetworkOnly (mutation queue handles offline)
          { urlPattern: /\/api\/(workout|weight|errors)$/, handler: 'NetworkOnly' },
          // /version.json — NetworkOnly (always fresh; powers update polling)
          { urlPattern: /\/version\.json$/, handler: 'NetworkOnly' },
        ],
      },
      devOptions: { enabled: false },
    }),
  ],
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
      '/version.json': {
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
    // Build-time injection — VITE_BUILD_HASH consumed by services/version.ts.
    __BUILD_HASH__: JSON.stringify(buildHash),
    'import.meta.env.VITE_BUILD_HASH': JSON.stringify(buildHash),
  },
});
