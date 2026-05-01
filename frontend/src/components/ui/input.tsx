// Input — UI-SPEC §6.1 Primitives.
// Min height 44px (UI-06). All colors via @theme tokens.
// Error state via aria-invalid (UI-15: never red border alone — paired with role="alert"
// + Italian copy + icon at FormField composition layer).
import * as React from 'react';
import { cn } from '@/lib/cn';

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(
          'flex h-11 w-full',
          'rounded-[var(--radius-md)] border border-[var(--color-input)]',
          'bg-[var(--color-bg-elev)] text-[var(--color-text)] text-[var(--text-base)]',
          'px-3 py-2',
          'placeholder:text-[var(--color-neutral-400)]',
          'shadow-[var(--shadow-1)]',
          'transition-[border-color,box-shadow] duration-[var(--duration-fast)] ease-[var(--ease-out-soft)]',
          'focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--color-bg)] focus-visible:outline-none',
          'disabled:cursor-not-allowed disabled:opacity-50',
          'file:border-0 file:bg-transparent file:font-semibold file:text-[var(--text-caption)]',
          'aria-invalid:border-[var(--color-destructive)] aria-invalid:ring-1 aria-invalid:ring-[var(--color-destructive)]',
          className,
        )}
        {...props}
      />
    );
  },
);
Input.displayName = 'Input';

export { Input };
