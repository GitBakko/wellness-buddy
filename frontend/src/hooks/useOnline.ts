// frontend/src/hooks/useOnline.ts
// Wraps navigator.onLine + online/offline events.
// Used by SyncStatusPip (UI-SPEC §10.5) and offline-first form submission flows.
// D-19: offline error UX — toast on first offline mutation.

import { useEffect, useState } from 'react';

export function useOnline(): boolean {
  const [online, setOnline] = useState<boolean>(() => {
    if (typeof navigator === 'undefined') return true;
    return navigator.onLine;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handleOnline = () => setOnline(true);
    const handleOffline = () => setOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return online;
}
