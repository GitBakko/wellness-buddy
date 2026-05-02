// frontend/src/components/week/WeekPicker.tsx
// Plan 02-02 — week navigator: 5-chip horizontal row (current ± 2) + jump-to-date popover.
//
// UI-SPEC §6.2 anatomy:
//   ┌──────────────────────────────────────────────────────────────┐
//   │  [chip] [chip] [chip:active] [chip] [chip]   [📅 jump btn]  │
//   └──────────────────────────────────────────────────────────────┘
//   - 5 chips horizontal, scroll-snap-x; each chip ≥44px hit, --radius-pill
//   - Active chip: --color-leaf-100 background, --color-text label
//   - Inactive chip: --color-surface-muted background, --color-text-muted label
//   - CalendarBlank IconButton 44×44 → Radix Popover with month-grid date picker
//   - Picking any date routes to startOfWeek(date, { weekStartsOn: 1 })
//
// All copy from copy.it.ts week.* namespace; all colors via @theme tokens.

import * as React from 'react';
import * as PopoverPrimitive from '@radix-ui/react-popover';
import { addWeeks, format, startOfWeek, subWeeks } from 'date-fns';

import { CalendarBlank } from '@/components/icons';
import { Calendar } from '@/components/ui/calendar';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';
import { italianDateShort } from '@/lib/format';

export interface WeekPickerProps {
  /** Current selected weekStart in YYYY-MM-DD (Monday). */
  value: string;
  /** Called with the new weekStart in YYYY-MM-DD when chips or popover pick a different week. */
  onChange: (weekStart: string) => void;
}

function fmtIso(d: Date): string {
  return format(d, 'yyyy-MM-dd');
}

function chipWeekStarts(currentMonday: Date): Date[] {
  // current ± 2 weeks → 5 entries (oldest first → newest)
  return [
    subWeeks(currentMonday, 2),
    subWeeks(currentMonday, 1),
    currentMonday,
    addWeeks(currentMonday, 1),
    addWeeks(currentMonday, 2),
  ];
}

export function WeekPicker({
  value,
  onChange,
}: WeekPickerProps): React.ReactElement {
  // Parse YYYY-MM-DD as a local-date Monday (weekStartsOn: 1).
  // We construct the date at noon to dodge any DST surprises.
  const currentMonday = React.useMemo(() => {
    const [y, m, d] = value.split('-').map(Number);
    return new Date(y, (m ?? 1) - 1, d ?? 1, 12, 0, 0);
  }, [value]);

  const chips = React.useMemo(
    () => chipWeekStarts(currentMonday),
    [currentMonday],
  );

  const [popoverOpen, setPopoverOpen] = React.useState(false);

  const handleChipPick = (monday: Date) => {
    const iso = fmtIso(monday);
    if (iso !== value) onChange(iso);
  };

  const handleDatePick = (picked: Date | undefined) => {
    if (!picked) return;
    const monday = startOfWeek(picked, { weekStartsOn: 1 });
    const iso = fmtIso(monday);
    setPopoverOpen(false);
    if (iso !== value) onChange(iso);
  };

  return (
    <div
      className="flex items-center gap-[var(--spacing-2)] overflow-x-auto py-[var(--spacing-1)]"
      role="group"
      aria-label={copy.week.weekPickerCurrentLabel}
    >
      <div
        className="flex gap-[var(--spacing-2)] flex-1 min-w-0 overflow-x-auto"
        style={{ scrollSnapType: 'x mandatory' }}
      >
        {chips.map((monday) => {
          const iso = fmtIso(monday);
          const isActive = iso === value;
          const label = italianDateShort(monday);
          return (
            <button
              key={iso}
              type="button"
              onClick={() => handleChipPick(monday)}
              data-active={isActive ? 'true' : undefined}
              aria-current={isActive ? 'date' : undefined}
              className={cn(
                'inline-flex items-center justify-center flex-shrink-0',
                'px-[var(--spacing-4)] py-[var(--spacing-2)]',
                'rounded-[var(--radius-pill)]',
                'min-h-11',
                'text-[length:var(--text-caption)] font-semibold',
                'transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)]',
                'active:scale-[0.97]',
              )}
              style={{
                background: isActive
                  ? 'var(--color-leaf-100)'
                  : 'var(--color-surface-muted)',
                color: isActive
                  ? 'var(--color-text)'
                  : 'var(--color-text-muted)',
                scrollSnapAlign: 'center',
              }}
            >
              {label}
            </button>
          );
        })}
      </div>
      <PopoverPrimitive.Root open={popoverOpen} onOpenChange={setPopoverOpen}>
        <PopoverPrimitive.Trigger asChild>
          <button
            type="button"
            aria-label={copy.week.weekPickerJumpAria}
            className={cn(
              'inline-flex items-center justify-center flex-shrink-0',
              'w-11 h-11 rounded-[var(--radius-pill)]',
              'bg-[var(--color-surface-muted)] text-[color:var(--color-text-muted)]',
              'transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)]',
              'active:scale-[0.97]',
            )}
          >
            <CalendarBlank size={22} weight="regular" aria-hidden="true" />
          </button>
        </PopoverPrimitive.Trigger>
        <PopoverPrimitive.Portal>
          <PopoverPrimitive.Content
            align="end"
            sideOffset={8}
            className={cn(
              'z-50 rounded-[var(--radius-md)]',
              'border border-[var(--color-border)]',
              'bg-[var(--color-surface)] shadow-[var(--shadow-2)]',
            )}
          >
            <Calendar
              mode="single"
              selected={currentMonday}
              onSelect={handleDatePick}
              showOutsideDays
              weekStartsOn={1}
            />
          </PopoverPrimitive.Content>
        </PopoverPrimitive.Portal>
      </PopoverPrimitive.Root>
    </div>
  );
}
