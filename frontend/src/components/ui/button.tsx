// Button — UI-SPEC §6.1 Primitives.
// Variants: primary | secondary | ghost | destructive (link added for in-paragraph use).
// States: default / hover / pressed / disabled / loading.
// Tap microinteraction (UI-04 #6): scale 0.97 over 80ms ease-out-soft on press.
// Min height 44px (UI-06 touch target).
// All colors via @theme tokens (UI-01) — vanilla shadcn rejected (UI-03).
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

const buttonVariants = cva(
  // Base — every variant inherits these
  [
    'inline-flex items-center justify-center gap-2 whitespace-nowrap',
    'rounded-[var(--radius-button)] font-sans font-semibold',
    'min-h-11', // 44px touch target (UI-06)
    'select-none outline-none',
    'transition-[transform,background-color,color,box-shadow] duration-[var(--duration-fast)] ease-[var(--ease-out-soft)]',
    // Tap microinteraction — UI-04 #6
    'active:scale-[calc(1-0.03*var(--motion-scale))]',
    'active:transition-transform active:duration-[var(--duration-instant)]',
    // Focus ring — UI-13
    'focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg)]',
    // Disabled
    'disabled:pointer-events-none disabled:opacity-50',
    // Icon sizing
    "[&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-5 [&_svg]:shrink-0",
  ],
  {
    variants: {
      variant: {
        primary: [
          'bg-[var(--color-coral-500)] text-[var(--color-primary-foreground)]',
          'hover:bg-[var(--color-coral-600)]',
          'shadow-[var(--shadow-1)]',
        ],
        secondary: [
          'bg-[var(--color-secondary)] text-[var(--color-secondary-foreground)]',
          'hover:bg-[var(--color-surface-muted)]',
          'border border-[var(--color-border)]',
        ],
        ghost: ['bg-transparent text-[var(--color-text)]', 'hover:bg-[var(--color-surface-muted)]'],
        destructive: [
          'bg-[var(--color-destructive)] text-[var(--color-primary-foreground)]',
          'hover:opacity-90',
          'shadow-[var(--shadow-1)]',
        ],
        link: [
          'bg-transparent text-[var(--color-coral-700)] underline-offset-4',
          'hover:underline min-h-0',
        ],
        outline: [
          'bg-[var(--color-bg-elev)] text-[var(--color-text)]',
          'border border-[var(--color-border)]',
          'hover:bg-[var(--color-surface-muted)]',
        ],
      },
      size: {
        default: 'h-11 px-4 py-2 text-[var(--text-base)]',
        sm: 'h-9 px-3 text-[var(--text-caption)]',
        lg: 'h-12 px-6 text-[var(--text-base)]',
        icon: 'size-11 p-0', // 44x44 — UI-SPEC §6.1 IconButton
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'default',
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp ref={ref} className={cn(buttonVariants({ variant, size, className }))} {...props} />
    );
  },
);
Button.displayName = 'Button';

export { Button, buttonVariants };
