// frontend/src/components/layout/UpdatePromptToast.tsx
// Mounts useVersionPolling at AppShell scope. Renders nothing —
// the actual UI lives in sonner toast triggered from version.ts.
import { useVersionPolling } from '@/services/version';

export function UpdatePromptToast(): null {
  useVersionPolling();
  return null;
}
