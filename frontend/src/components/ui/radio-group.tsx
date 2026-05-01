// RadioGroup — UI-SPEC §6.1 Primitives.
// Used in workout type, theme picker.
import * as React from 'react';
import * as RadioGroupPrimitive from '@radix-ui/react-radio-group';
import { Circle } from 'lucide-react';
import { cn } from '@/lib/cn';

const RadioGroup = React.forwardRef<
  React.ComponentRef<typeof RadioGroupPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Root>
>(({ className, ...props }, ref) => (
  <RadioGroupPrimitive.Root ref={ref} className={cn('grid gap-2', className)} {...props} />
));
RadioGroup.displayName = RadioGroupPrimitive.Root.displayName;

const RadioGroupItem = React.forwardRef<
  React.ComponentRef<typeof RadioGroupPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item>
>(({ className, ...props }, ref) => (
  <RadioGroupPrimitive.Item
    ref={ref}
    className={cn(
      // 44x44 hit area wraps a 24x24 circle visual (UI-06)
      'group relative inline-flex size-11 items-center justify-center',
      'cursor-pointer select-none',
      'before:absolute before:size-6 before:rounded-[var(--radius-pill)]',
      'before:border-2 before:border-[var(--color-neutral-400)]',
      'before:bg-[var(--color-bg-elev)]',
      'before:transition-[border-color] before:duration-[var(--duration-fast)] before:ease-[var(--ease-out-soft)]',
      'data-[state=checked]:before:border-[var(--color-coral-500)]',
      'hover:before:border-[var(--color-neutral-500)]',
      'focus-visible:outline-none focus-visible:before:ring-2 focus-visible:before:ring-[var(--color-focus-ring)] focus-visible:before:ring-offset-2 focus-visible:before:ring-offset-[var(--color-bg)]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      className,
    )}
    {...props}
  >
    <RadioGroupPrimitive.Indicator className="relative z-10 flex items-center justify-center">
      <Circle
        className="size-2.5 fill-[var(--color-coral-500)] text-[var(--color-coral-500)]"
        aria-hidden="true"
      />
    </RadioGroupPrimitive.Indicator>
  </RadioGroupPrimitive.Item>
));
RadioGroupItem.displayName = RadioGroupPrimitive.Item.displayName;

export { RadioGroup, RadioGroupItem };
