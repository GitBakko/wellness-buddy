// Sheet — UI-SPEC §6.2 Composites.
// Bottom sheet on mobile, side dialog on desktop (≥768px).
// Close on swipe-down + Esc + scrim tap. Safe-area aware.
import * as React from 'react';
import * as SheetPrimitive from '@radix-ui/react-dialog';
import { cva, type VariantProps } from 'class-variance-authority';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';

const Sheet = SheetPrimitive.Root;
const SheetTrigger = SheetPrimitive.Trigger;
const SheetClose = SheetPrimitive.Close;
const SheetPortal = SheetPrimitive.Portal;

const SheetOverlay = React.forwardRef<
  React.ComponentRef<typeof SheetPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof SheetPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <SheetPrimitive.Overlay
    ref={ref}
    className={cn(
      'fixed inset-0 z-50',
      'bg-[var(--color-neutral-900)]/50 backdrop-blur-sm',
      'data-[state=open]:animate-in data-[state=closed]:animate-out',
      'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
      'duration-[var(--duration-base)]',
      className,
    )}
    {...props}
  />
));
SheetOverlay.displayName = SheetPrimitive.Overlay.displayName;

const sheetVariants = cva(
  [
    'fixed z-50 gap-4',
    'bg-[var(--color-bg-elev)] text-[var(--color-text)]',
    'shadow-[var(--shadow-3)]',
    'transition ease-[var(--ease-out-soft)]',
    'data-[state=open]:animate-in data-[state=closed]:animate-out',
    'data-[state=closed]:duration-[var(--duration-fast)]',
    'data-[state=open]:duration-[var(--duration-base)]',
  ],
  {
    variants: {
      side: {
        top: [
          'inset-x-0 top-0',
          'rounded-b-[var(--radius-sheet)]',
          'data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top',
          'pt-[max(var(--spacing-6),env(safe-area-inset-top))]',
        ],
        bottom: [
          'inset-x-0 bottom-0',
          'rounded-t-[var(--radius-sheet)]',
          'data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom',
          'pb-[max(var(--spacing-6),env(safe-area-inset-bottom))]',
          'p-6',
        ],
        left: [
          'inset-y-0 left-0 h-full w-3/4 sm:max-w-sm',
          'rounded-r-[var(--radius-sheet)]',
          'data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left',
          'p-6',
        ],
        right: [
          'inset-y-0 right-0 h-full w-3/4 sm:max-w-sm',
          'rounded-l-[var(--radius-sheet)]',
          'data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right',
          'p-6',
        ],
      },
    },
    defaultVariants: { side: 'right' },
  },
);

interface SheetContentProps
  extends
    React.ComponentPropsWithoutRef<typeof SheetPrimitive.Content>,
    VariantProps<typeof sheetVariants> {}

const SheetContent = React.forwardRef<
  React.ComponentRef<typeof SheetPrimitive.Content>,
  SheetContentProps
>(({ side = 'right', className, children, ...props }, ref) => (
  <SheetPortal>
    <SheetOverlay />
    <SheetPrimitive.Content ref={ref} className={cn(sheetVariants({ side }), className)} {...props}>
      {children}
      <SheetPrimitive.Close
        className={cn(
          'absolute top-4 right-4',
          'inline-flex size-11 items-center justify-center',
          'rounded-[var(--radius-pill)] text-[var(--color-text-muted)]',
          'transition-colors duration-[var(--duration-fast)]',
          'hover:bg-[var(--color-surface-muted)] hover:text-[var(--color-text)]',
          'focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)] focus-visible:outline-none',
        )}
      >
        <X className="size-5" aria-hidden="true" />
        <span className="sr-only">Chiudi</span>
      </SheetPrimitive.Close>
    </SheetPrimitive.Content>
  </SheetPortal>
));
SheetContent.displayName = SheetPrimitive.Content.displayName;

const SheetHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex flex-col gap-2 text-center sm:text-left', className)} {...props} />
);
SheetHeader.displayName = 'SheetHeader';

const SheetFooter = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn('flex flex-col-reverse gap-2 sm:flex-row sm:justify-end', className)}
    {...props}
  />
);
SheetFooter.displayName = 'SheetFooter';

const SheetTitle = React.forwardRef<
  React.ComponentRef<typeof SheetPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof SheetPrimitive.Title>
>(({ className, ...props }, ref) => (
  <SheetPrimitive.Title
    ref={ref}
    className={cn('font-semibold text-[var(--color-text)] text-[var(--text-heading)]', className)}
    {...props}
  />
));
SheetTitle.displayName = SheetPrimitive.Title.displayName;

const SheetDescription = React.forwardRef<
  React.ComponentRef<typeof SheetPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof SheetPrimitive.Description>
>(({ className, ...props }, ref) => (
  <SheetPrimitive.Description
    ref={ref}
    className={cn('text-[var(--color-text-muted)] text-[var(--text-base)]', className)}
    {...props}
  />
));
SheetDescription.displayName = SheetPrimitive.Description.displayName;

export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription,
};
