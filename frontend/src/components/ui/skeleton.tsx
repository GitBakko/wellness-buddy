// Skeleton — UI-SPEC §6 + §11.1 Loading rules.
// Shimmering bars matching final layout shape. NEVER spinner-only on data screens.
// Linear easing is the only allowed exception (UI-SPEC §5).
import * as React from 'react';
import { cn } from '@/lib/cn';

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'animate-pulse',
        'rounded-[var(--radius-sm)] bg-[var(--color-surface-muted)]',
        className,
      )}
      {...props}
    />
  );
}

export { Skeleton };
