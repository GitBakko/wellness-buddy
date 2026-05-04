// Calendar — UI-SPEC §6 (uses react-day-picker v9 + brand tokens).
// Italian locale, Monday-first, IT date conventions (UI-SPEC §3.5).
//
// react-day-picker v9 renamed all classNames keys vs v8. Keys must match the
// `UI`/`DayFlag`/`SelectionState` enums from `react-day-picker/dist/esm/UI.d.ts`.
import * as React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { DayPicker } from 'react-day-picker';
import { it } from 'date-fns/locale';
import { cn } from '@/lib/cn';
import { buttonVariants } from '@/components/ui/button';

export type CalendarProps = React.ComponentProps<typeof DayPicker>;

function Calendar({ className, classNames, showOutsideDays = true, ...props }: CalendarProps) {
  return (
    <DayPicker
      locale={it}
      weekStartsOn={1}
      showOutsideDays={showOutsideDays}
      className={cn('p-3', className)}
      classNames={{
        root: 'rdp-root',
        months: 'flex flex-col sm:flex-row gap-4',
        month: 'flex flex-col gap-3',
        month_caption: 'flex justify-center pt-1 relative items-center h-9',
        caption_label:
          'text-[length:var(--text-base)] font-semibold text-[var(--color-text)] capitalize',
        nav: 'flex items-center justify-between absolute inset-x-0 top-1 px-1',
        button_previous: cn(
          buttonVariants({ variant: 'ghost', size: 'icon' }),
          'size-9 bg-transparent p-0 opacity-70 hover:opacity-100',
        ),
        button_next: cn(
          buttonVariants({ variant: 'ghost', size: 'icon' }),
          'size-9 bg-transparent p-0 opacity-70 hover:opacity-100',
        ),
        month_grid: 'w-full border-collapse',
        weekdays: 'grid grid-cols-7 mb-1',
        weekday:
          'text-[var(--color-text-muted)] text-[length:var(--text-caption)] font-medium uppercase tracking-wide text-center h-8 flex items-center justify-center',
        weeks: 'flex flex-col gap-1',
        week: 'grid grid-cols-7',
        day: cn(
          'relative p-0 text-center text-[length:var(--text-base)]',
          'focus-within:relative focus-within:z-20',
        ),
        day_button: cn(
          buttonVariants({ variant: 'ghost' }),
          'size-9 p-0 font-normal aria-selected:opacity-100 mx-auto',
        ),
        selected:
          '[&>button]:bg-[var(--color-coral-500)] [&>button]:text-[var(--color-primary-foreground)] [&>button:hover]:bg-[var(--color-coral-600)] [&>button:focus]:bg-[var(--color-coral-600)]',
        today:
          '[&>button]:bg-[var(--color-surface-muted)] [&>button]:text-[var(--color-text)] [&>button]:font-semibold',
        outside: '[&>button]:text-[var(--color-neutral-400)] [&>button]:opacity-50',
        disabled: '[&>button]:text-[var(--color-neutral-400)] [&>button]:opacity-50',
        hidden: 'invisible',
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
