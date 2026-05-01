// frontend/src/hooks/useToast.ts
// Re-export sonner's toast for app-wide use.
// Sonner is the shadcn/ui default — accessible (role="status"/"alert"),
// supports rich-color variants, dismissible, no auto-dismiss for update toast (UI-SPEC §10.2).
//
// Italian copy comes from `@/i18n/copy.it.ts` — never inline strings here.

export { toast, Toaster } from 'sonner';
