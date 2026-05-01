// Calendar — UI-SPEC §6 (uses react-day-picker v9 + brand tokens).
// Italian locale, IT date conventions (UI-SPEC §3.5).
import * as React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { DayPicker } from 'react-day-picker';
import { cn } from '@/lib/cn';
import { buttonVariants } from '@/components/ui/button';

export type CalendarProps = React.ComponentProps<typeof DayPicker>;

function Calendar({ className, classNames, showOutsideDays = true, ...props }: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn('p-3', className)}
      classNames={{
        months: 'flex flex-col sm:flex-row gap-4',
        month: 'flex flex-col gap-3',
        caption: 'flex justify-center pt-1 relative items-center',
        caption_label: 'text-[var(--text-base)] font-semibold text-[var(--color-text)]',
        nav: 'flex items-center gap-1',
        nav_button: cn(
          buttonVariants({ variant: 'ghost', size: 'icon' }),
          'size-8 bg-transparent p-0 opacity-70 hover:opacity-100',
        ),
        nav_button_previous: 'absolute left-1',
        nav_button_next: 'absolute right-1',
        table: 'w-full border-collapse',
        head_row: 'flex',
        head_cell:
          'text-[var(--color-text-muted)] rounded-[var(--radius-sm)] w-9 font-normal text-[var(--text-caption)]',
        row: 'flex w-full mt-2',
        cell: cn(
          'relative p-0 text-center text-[var(--text-base)]',
          'focus-within:relative focus-within:z-20',
          'first:[&:has([aria-selected])]:rounded-l-[var(--radius-sm)] last:[&:has([aria-selected])]:rounded-r-[var(--radius-sm)]',
        ),
        day: cn(
          buttonVariants({ variant: 'ghost' }),
          'size-9 p-0 font-normal aria-selected:opacity-100',
        ),
        day_selected:
          'bg-[var(--color-coral-500)] text-[var(--color-primary-foreground)] hover:bg-[var(--color-coral-600)] focus:bg-[var(--color-coral-600)]',
        day_today: 'bg-[var(--color-surface-muted)] text-[var(--color-text)] font-semibold',
        day_outside: 'text-[var(--color-neutral-400)] opacity-50',
        day_disabled: 'text-[var(--color-neutral-400)] opacity-50',
        day_range_middle:
          'aria-selected:bg-[var(--color-surface-muted)] aria-selected:text-[var(--color-text)]',
        day_hidden: 'invisible',
        ...classNames,
      }}
      components={{
        Chevron: ({ orientation, ...rest }) =>
          orientation === 'left' ? (
            <ChevronLeft className="size-4" aria-hidden="true" {...rest} />
          ) : (
            <ChevronRight className="size-4" aria-hidden="true" {...rest} />
          ),
      }}
      {...props}
    />
  );
}
Calendar.displayName = 'Calendar';

export { Calendar };
