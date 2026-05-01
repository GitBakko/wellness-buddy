// frontend/src/components/layout/SyncStatusPip.tsx
// UI-SPEC §10.5 — sync status pip in AppBar.
// PITFALLS #1 trust signal: shows online/offline + pending count + last sync time.
// Three states (color-coded but with text label too — UI-13 never color alone):
//   - Offline:  neutral dot + "Offline"
//   - Pending:  warning dot + "In sincronizzazione (N)"
//   - Synced:   success dot + "Sincronizzato"
import { useSyncStore } from '@/stores/sync';
import { copy } from '@/i18n/copy.it';
import { italianTime } from '@/lib/format';

export function SyncStatusPip() {
  const online = useSyncStore((s) => s.online);
  const pendingMutations = useSyncStore((s) => s.pendingMutations);
  const lastSyncedAt = useSyncStore((s) => s.lastSyncedAt);

  const tooltip = lastSyncedAt
    ? copy.sync.tooltip.replace('{time}', italianTime(new Date(lastSyncedAt)))
    : copy.sync.synced;

  const status = !online
    ? copy.sync.offline
    : pendingMutations > 0
      ? `${copy.sync.pending} (${pendingMutations})`
      : copy.sync.synced;

  const dotColor = !online
    ? 'var(--color-neutral-500)'
    : pendingMutations > 0
      ? 'var(--color-warning)'
      : 'var(--color-success)';

  return (
    <div
      className="flex items-center gap-[var(--spacing-2)]"
      title={tooltip}
      role="status"
      aria-live="polite"
    >
      <span
        aria-hidden="true"
        className="w-2 h-2 rounded-[var(--radius-pill)]"
        style={{ background: dotColor }}
      />
      <span className="text-[var(--text-caption)] sr-only md:not-sr-only">
        {status}
      </span>
    </div>
  );
}
