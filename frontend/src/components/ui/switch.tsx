// Switch — UI-SPEC §6.1 Primitives.
// iOS-style switch motion, 250ms ease-out-soft.
import * as React from 'react';
import * as SwitchPrimitive from '@radix-ui/react-switch';
import { cn } from '@/lib/cn';

const Switch = React.forwardRef<
  React.ComponentRef<typeof SwitchPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitive.Root>
>(({ className, ...props }, ref) => (
  <SwitchPrimitive.Root
    ref={ref}
    className={cn(
      'peer inline-flex h-7 w-12 shrink-0 cursor-pointer items-center',
      'rounded-[var(--radius-pill)] border-2 border-transparent',
      'transition-colors duration-[var(--duration-base)] ease-[var(--ease-out-soft)]',
      'focus-visible:ring-2 focus-visible:ring-[var(--color-focus-ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg)] focus-visible:outline-none',
      'data-[state=checked]:bg-[var(--color-coral-500)]',
      'data-[state=unchecked]:bg-[var(--color-neutral-300)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      className,
    )}
    {...props}
  >
    <SwitchPrimitive.Thumb
      className={cn(
        'pointer-events-none block size-5 rounded-[var(--radius-pill)]',
        'bg-[var(--color-bg-elev)] shadow-[var(--shadow-1)]',
        'ring-0 transition-transform duration-[var(--duration-base)] ease-[var(--ease-out-soft)]',
        'data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0',
      )}
    />
  </SwitchPrimitive.Root>
));
Switch.displayName = SwitchPrimitive.Root.displayName;

export { Switch };
