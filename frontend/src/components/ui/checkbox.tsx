// Checkbox — UI-SPEC §6.1 Primitives.
// Hit area 44×44 wrapping 24×24 visual. Tick draw 200ms (under motion budget).
// Indeterminate state visually distinct from checked.
import * as React from 'react';
import * as CheckboxPrimitive from '@radix-ui/react-checkbox';
import { Check, Minus } from 'lucide-react';
import { cn } from '@/lib/cn';

const Checkbox = React.forwardRef<
  React.ComponentRef<typeof CheckboxPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root>
>(({ className, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(
      // 44x44 hit area, 24x24 visual via inner padding (UI-06)
      'group relative inline-flex size-11 items-center justify-center',
      'cursor-pointer select-none',
      'before:absolute before:size-6 before:rounded-[var(--radius-sm)]',
      'before:border-2 before:border-[var(--color-neutral-400)]',
      'before:bg-[var(--color-bg-elev)]',
      'before:transition-[background-color,border-color] before:duration-[var(--duration-fast)] before:ease-[var(--ease-out-soft)]',
      'data-[state=checked]:before:border-[var(--color-coral-500)] data-[state=checked]:before:bg-[var(--color-coral-500)]',
      'data-[state=indeterminate]:before:border-[var(--color-coral-500)] data-[state=indeterminate]:before:bg-[var(--color-coral-500)]',
      'hover:before:border-[var(--color-neutral-500)]',
      'data-[state=checked]:hover:before:bg-[var(--color-coral-600)]',
      'focus-visible:outline-none focus-visible:before:ring-2 focus-visible:before:ring-[var(--color-focus-ring)] focus-visible:before:ring-offset-2 focus-visible:before:ring-offset-[var(--color-bg)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'active:scale-[calc(1-0.03*var(--motion-scale))] active:transition-transform active:duration-[var(--duration-instant)]',
      className,
    )}
    {...props}
  >
    <CheckboxPrimitive.Indicator className="relative z-10 flex items-center justify-center text-[var(--color-primary-foreground)]">
      {props.checked === 'indeterminate' ? (
        <Minus className="size-4" strokeWidth={2.5} aria-hidden="true" />
      ) : (
        <Check className="size-4" strokeWidth={2.5} aria-hidden="true" />
      )}
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
));
Checkbox.displayName = CheckboxPrimitive.Root.displayName;

export { Checkbox };
