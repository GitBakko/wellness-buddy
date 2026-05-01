// Toaster — UI-SPEC §6.2 Composites.
// Sonner with custom-styled to brand palette. Variants: success / error / info.
// Auto-dismiss 4s default, 6s for errors, indefinite for "Nuova versione disponibile".
import { Toaster as SonnerToaster, type ToasterProps } from 'sonner';

function Toaster(props: ToasterProps) {
  return (
    <SonnerToaster
      position="top-right"
      richColors
      closeButton
      duration={4000}
      toastOptions={{
        classNames: {
          toast:
            'bg-[var(--color-bg-elev)] text-[var(--color-text)] border border-[var(--color-border)] rounded-[var(--radius-md)] shadow-[var(--shadow-2)]',
          title: 'text-[var(--text-base)] font-semibold',
          description: 'text-[var(--text-caption)] text-[var(--color-text-muted)]',
          actionButton:
            'bg-[var(--color-coral-500)] text-[var(--color-primary-foreground)] rounded-[var(--radius-button)]',
          cancelButton:
            'bg-[var(--color-surface-muted)] text-[var(--color-text)] rounded-[var(--radius-button)]',
          success: 'border-l-4 border-l-[var(--color-success)]',
          error: 'border-l-4 border-l-[var(--color-destructive)]',
          warning: 'border-l-4 border-l-[var(--color-warning)]',
        },
      }}
      {...props}
    />
  );
}

export { Toaster };
