// Tooltip — UI-SPEC §6 (Plan 02-07: SharedBadge surfaces "Aggiornato da {nome}").
// Radix-based primitive matching the rest of the shadcn/ui style; tokens-only,
// no hardcoded hex (CLAUDE.md UI rule 1).
import * as React from 'react';
import * as TooltipPrimitive from '@radix-ui/react-tooltip';

import { cn } from '@/lib/cn';

const TooltipProvider = TooltipPrimitive.Provider;
const Tooltip = TooltipPrimitive.Root;
const TooltipTrigger = TooltipPrimitive.Trigger;

const TooltipContent = React.forwardRef<
  React.ComponentRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Portal>
    <TooltipPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        'z-50 overflow-hidden',
        'rounded-[var(--radius-sm)] border border-[var(--color-border)]',
        'bg-[var(--color-popover)] text-[color:var(--color-popover-foreground)]',
        'px-[var(--spacing-2)] py-[var(--spacing-1)] shadow-[var(--shadow-1)]',
        'text-[var(--text-caption)] leading-[var(--leading-caption)]',
        'data-[state=closed]:animate-out data-[state=closed]:fade-out-0',
        'data-[state=closed]:zoom-out-95 data-[state=delayed-open]:animate-in',
        'data-[state=delayed-open]:fade-in-0 data-[state=delayed-open]:zoom-in-95',
        'data-[side=top]:slide-in-from-bottom-1 data-[side=bottom]:slide-in-from-top-1',
        'data-[side=left]:slide-in-from-right-1 data-[side=right]:slide-in-from-left-1',
        className,
      )}
      {...props}
    />
  </TooltipPrimitive.Portal>
));
TooltipContent.displayName = TooltipPrimitive.Content.displayName;

export { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger };
