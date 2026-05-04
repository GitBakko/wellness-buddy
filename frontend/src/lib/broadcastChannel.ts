// frontend/src/lib/broadcastChannel.ts
// D-25 — multi-tab shopping list sync.
//
// Two-tier strategy (Pitfall #15):
//   1. BroadcastChannel where supported (modern Chromium / Firefox / Safari 15.4+).
//   2. ``window.focus`` listener fallback for iOS Safari Private mode where
//      BroadcastChannel exists but ``new BroadcastChannel`` throws SecurityError
//      OR where the API is missing entirely.
//
// The fallback re-fetches when the user returns to a tab — slower than push
// but invisible in practice because the user only sees one tab at a time.

type Listener<T> = (msg: T) => void;

/**
 * Subscribe to a named channel. Returns an unsubscribe function.
 *
 * The listener receives the raw payload pushed by ``postSyncMessage``. In the
 * focus-fallback path, the listener receives ``{ type: 'focus_refetch' }`` —
 * callers should treat that as "invalidate everything and re-fetch".
 */
export function createSyncChannel<T>(name: string, listener: Listener<T>): () => void {
  if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
    try {
      const bc = new BroadcastChannel(name);
      const handler = (e: MessageEvent<T>) => listener(e.data);
      bc.addEventListener('message', handler);
      return () => {
        bc.removeEventListener('message', handler);
        bc.close();
      };
    } catch {
      // SecurityError in Safari Private mode — fall through to focus fallback.
    }
  }
  if (typeof window === 'undefined') {
    return () => {};
  }
  const onFocus = () => listener({ type: 'focus_refetch' } as unknown as T);
  window.addEventListener('focus', onFocus);
  return () => window.removeEventListener('focus', onFocus);
}

/**
 * Push a sync message on a named channel.
 *
 * Silent no-op when BroadcastChannel is unavailable or throws — in that case
 * other tabs receive the message via their own ``focus`` event when they
 * regain focus. A "missed" message in private mode means the user just sees
 * stale data until next focus, which is acceptable per D-25.
 */
export function postSyncMessage<T>(name: string, msg: T): void {
  if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
    try {
      const bc = new BroadcastChannel(name);
      try {
        bc.postMessage(msg);
      } finally {
        bc.close();
      }
    } catch {
      // Private-mode no-op — focus fallback in OTHER tab triggers the refetch.
    }
  }
}
