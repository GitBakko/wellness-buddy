// frontend/src/hooks/useUpdateToast.ts
// Re-export of useVersionPolling under the name AppShell expects.
// Mounted once via UpdatePromptToast component (renders nothing).
export { useVersionPolling as useUpdateToast } from '@/services/version';
