/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/react" />
/// <reference types="vite-plugin-pwa/client" />

declare module '*.css';
declare module '*.svg';
declare module '*.png';
declare module '*.woff2';
declare module '*.woff';

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_BUILD_HASH?: string;
  readonly VITE_APP_VERSION?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare const __BUILD_HASH__: string;
