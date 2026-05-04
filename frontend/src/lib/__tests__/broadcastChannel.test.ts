// frontend/src/lib/__tests__/broadcastChannel.test.ts
// Plan 02-05 — locks the multi-tab sync wiring (D-25, Pitfall #15).
//
// Tests run in jsdom; happy-dom doesn't ship BroadcastChannel either, so we
// stub a tiny in-memory implementation to verify the listener path. The
// fallback path is verified by deleting BroadcastChannel from window.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createSyncChannel, postSyncMessage } from '@/lib/broadcastChannel';

describe('broadcastChannel', () => {
  const originalBC = (globalThis as { BroadcastChannel?: unknown }).BroadcastChannel;

  beforeEach(() => {
    // Minimal in-memory BroadcastChannel mock that connects channels by name.
    const registry = new Map<string, Set<(e: MessageEvent) => void>>();
    class MockBC {
      name: string;
      private handlers = new Set<(e: MessageEvent) => void>();
      constructor(name: string) {
        this.name = name;
        const set = registry.get(name) ?? new Set();
        registry.set(name, set);
      }
      addEventListener(_t: 'message', cb: (e: MessageEvent) => void) {
        const set = registry.get(this.name)!;
        set.add(cb);
        this.handlers.add(cb);
      }
      removeEventListener(_t: 'message', cb: (e: MessageEvent) => void) {
        const set = registry.get(this.name);
        set?.delete(cb);
        this.handlers.delete(cb);
      }
      postMessage(data: unknown) {
        const set = registry.get(this.name);
        if (!set) return;
        for (const cb of set) {
          // Skip own subscribers — BroadcastChannel doesn't echo to sender.
          if (this.handlers.has(cb)) continue;
          cb({ data } as MessageEvent);
        }
      }
      close() {
        for (const cb of this.handlers) {
          registry.get(this.name)?.delete(cb);
        }
      }
    }
    (globalThis as { BroadcastChannel?: unknown }).BroadcastChannel = MockBC;
  });

  afterEach(() => {
    if (originalBC === undefined) {
      delete (globalThis as { BroadcastChannel?: unknown }).BroadcastChannel;
    } else {
      (globalThis as { BroadcastChannel?: unknown }).BroadcastChannel = originalBC;
    }
  });

  it('createSyncChannel + postSyncMessage delivers payload across tabs', () => {
    const listener = vi.fn();
    const unsub = createSyncChannel<{ type: string }>('test-chan', listener);
    postSyncMessage('test-chan', { type: 'updated' });
    expect(listener).toHaveBeenCalledWith({ type: 'updated' });
    unsub();
  });

  it('createSyncChannel returns an unsub function that removes the listener', () => {
    const listener = vi.fn();
    const unsub = createSyncChannel('test-chan', listener);
    unsub();
    postSyncMessage('test-chan', { type: 'updated' });
    expect(listener).not.toHaveBeenCalled();
  });

  it('falls back to focus listener when BroadcastChannel is unavailable', () => {
    delete (globalThis as { BroadcastChannel?: unknown }).BroadcastChannel;
    const listener = vi.fn();
    const unsub = createSyncChannel('test-chan', listener);
    window.dispatchEvent(new Event('focus'));
    expect(listener).toHaveBeenCalledTimes(1);
    expect(listener).toHaveBeenCalledWith({ type: 'focus_refetch' });
    unsub();
    window.dispatchEvent(new Event('focus'));
    // Listener already unsubscribed → call count unchanged.
    expect(listener).toHaveBeenCalledTimes(1);
  });
});
