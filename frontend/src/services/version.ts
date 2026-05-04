// frontend/src/services/version.ts
// Version polling + Workbox SW update flow (FND-06).
// Source: 01-RESEARCH.md Pattern 4 (frontend half).
//
// Two parallel update detection paths:
//
//   1. /version.json polling — every 5min + on visibilitychange. Cheap and
//      independent of SW; works even if Workbox skipped registration. When
//      remote.build_hash !== CURRENT_BUILD, show a sonner toast inviting
//      reload (copy.pwa.updateHeading = "Nuova versione disponibile").
//
//   2. virtual:pwa-register/react useRegisterSW — fires onRegisteredSW /
//      onNeedRefresh when Workbox has actually downloaded a new SW. The
//      same toast then calls updateServiceWorker(true) which posts
//      SKIP_WAITING and reloads.
//
// PITFALLS #2 — `skipWaiting: false` in vite.config.ts means the user
// controls the update via the toast (no auto-reload mid-form).

import { useEffect } from 'react';
import { useRegisterSW } from 'virtual:pwa-register/react';
import { toast } from 'sonner';
import { copy } from '@/i18n/copy.it';

const CURRENT_BUILD: string =
  (import.meta.env.VITE_BUILD_HASH as string | undefined) ?? 'dev';

const POLL_INTERVAL_MS = 5 * 60 * 1000;

// Plan 02-03 (gap closure): when CURRENT_BUILD === 'dev', the frontend was
// built without a real git SHA injection (no env var, no .git access — e.g.
// inside a sandboxed CI step or first-run dev environment). In that case
// every `/version.json` response will mismatch and produce a permanent
// "Nuova versione disponibile" toast loop. Skip polling entirely.
const SKIP_VERSION_POLLING = CURRENT_BUILD === 'dev' || import.meta.env.DEV;

interface VersionPayload {
  version?: string;
  build_hash: string;
}

async function fetchVersion(): Promise<string | null> {
  try {
    const r = await fetch('/version.json', { cache: 'no-store' });
    if (!r.ok) return null;
    const data = (await r.json()) as VersionPayload;
    return data.build_hash ?? null;
  } catch {
    return null;
  }
}

export function useVersionPolling(): void {
  const { updateServiceWorker } = useRegisterSW({
    onRegisterError(error: unknown) {
      console.error('SW registration failed', error);
    },
  });

  useEffect(() => {
    if (SKIP_VERSION_POLLING) return;
    let cancelled = false;
    let toastShown = false;

    function showUpdateToast() {
      if (toastShown) return;
      toastShown = true;
      toast.message(copy.pwa.updateHeading, {
        description: copy.pwa.updateBody,
        duration: Infinity,
        action: {
          label: copy.pwa.updateAction,
          onClick: () => updateServiceWorker(true),
        },
        cancel: {
          label: copy.pwa.updateDismiss,
          onClick: () => {
            /* postpone — next poll re-evaluates */
            toastShown = false;
          },
        },
      });
    }

    async function check() {
      if (document.hidden) return;
      const remote = await fetchVersion();
      if (!remote || cancelled) return;
      if (remote !== CURRENT_BUILD) {
        showUpdateToast();
      }
    }

    void check();
    const interval = setInterval(check, POLL_INTERVAL_MS);
    document.addEventListener('visibilitychange', check);
    return () => {
      cancelled = true;
      clearInterval(interval);
      document.removeEventListener('visibilitychange', check);
    };
  }, [updateServiceWorker]);
}
