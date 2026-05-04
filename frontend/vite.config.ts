// Vite 7 + React 19 + Tailwind 4 (@theme) + vite-plugin-pwa Workbox SW.
// Source: 01-RESEARCH.md Pattern 3 (vite-plugin-pwa) + 01-UI-SPEC.md §10.4 (manifest).
// PITFALLS #2 mitigation: NetworkFirst index.html with 3s timeout.
import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'node:path';
import fs from 'node:fs';
import { execSync } from 'node:child_process';

const appVersion = process.env.VITE_APP_VERSION ?? '0.2.0';
const buildHash = (() => {
  // Prefer explicit env var (set by deploy/scripts/package-release.ps1) so
  // the dist/version.json + JS bundle agree on the canonical SHA. Fallback
  // to live `git rev-parse` for `pnpm dev` and ad-hoc local builds.
  if (process.env.VITE_BUILD_HASH) return process.env.VITE_BUILD_HASH;
  try {
    return execSync('git rev-parse --short HEAD').toString().trim();
  } catch {
    return 'dev';
  }
})();

// Plan 02-03 (gap closure) — emit dist/version.json at build time so it
// agrees with the JS bundle's __BUILD_HASH__ baked-in value. Without this,
// public/version.json shipped a literal "dev" string and was copied verbatim
// to dist/, leaving the in-app update detector with mismatched hashes ⇒
// permanent "Nuova versione disponibile" toast on every visit. The backend
// /version.json proxy (web.config) still wins in prod when present, this
// emitted file is the dev/static fallback.
function versionJsonEmitter(): Plugin {
  return {
    name: 'wellness-buddy:version-json-emitter',
    apply: 'build',
    closeBundle() {
      const outFile = path.resolve(__dirname, 'dist/version.json');
      const payload = {
        version: appVersion,
        build_hash: buildHash,
      };
      fs.writeFileSync(outFile, JSON.stringify(payload, null, 2) + '\n', 'utf8');
      // eslint-disable-next-line no-console
      console.log(`[version-json] dist/version.json -> ${JSON.stringify(payload)}`);
    },
  };
}

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    versionJsonEmitter(),
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
      // dev only — prod uses IIS reverse proxy. Port 8001 chosen because
      // 8000 is reserved on this dev box for another service.
      '/api': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/version.json': {
        target: 'http://127.0.0.1:8002',
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
