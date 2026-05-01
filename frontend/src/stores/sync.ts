// frontend/src/stores/sync.ts
// Sync status store — backs SyncStatusPip (UI-SPEC §10.5, Pitfall #1).
//
//   - online:           navigator.onLine + online/offline events (set via useOnline + setOnline)
//   - pendingMutations: count of items in Dexie outbox awaiting flush (set by Plan 06 SW)
//   - lastSyncedAt:     epoch ms of last successful flush (null until first sync)
//
// This is the trust signal that prevents "this app deleted my data" support tickets
// when iOS evicts storage (RESEARCH note + UI-SPEC §10.5 — non-negotiable).

import { create } from 'zustand';

export interface SyncState {
  online: boolean;
  pendingMutations: number;
  lastSyncedAt: number | null;
  setOnline: (online: boolean) => void;
  setPending: (count: number) => void;
  setLastSyncedAt: (ts: number | null) => void;
}

export const useSyncStore = create<SyncState>((set) => ({
  online: typeof navigator !== 'undefined' ? navigator.onLine : true,
  pendingMutations: 0,
  lastSyncedAt: null,
  setOnline: (online) => set({ online }),
  setPending: (count) => set({ pendingMutations: count }),
  setLastSyncedAt: (ts) => set({ lastSyncedAt: ts }),
}));
