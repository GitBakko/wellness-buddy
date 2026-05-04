// frontend/src/pages/Shopping.tsx
// Plan 02-05 — /spesa route. SHOP-01..06, SHOP-08, D-25.
//
// Layout (UI-SPEC §6.3):
//   1. Header: "La spesa" heading + subtitle "settimana del {weekStartLong}"
//   2. ShoppingViewToggle (Per categoria | Per giorno)
//   3a. Per categoria → 5 ShoppingCategorySection (fixed order, collapsible)
//   3b. Per giorno    → 7 day sections, each with the same items grouped by
//       contributing meal slot (uses ShoppingItem.sources)
//   4. Sticky bottom row: [Reset settimana] [Copia testo] [Esporta PDF]
//
// Multi-tab sync (D-25): subscribes to wb-shopping-sync channel; any
// remote-tab change invalidates the local TanStack query.
//
// All copy from copy.it.ts shopping.* + sync.* + errors.* namespaces.

import * as React from 'react';
import { useParams } from 'react-router';
import { addDays, format, parseISO, startOfWeek } from 'date-fns';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import {
  ArrowCounterClockwise,
  ClipboardText,
  FilePdf,
} from '@/components/icons';
import { EmptyStateShopping } from '@/components/shopping/EmptyStateShopping';
import { ShoppingCategorySection } from '@/components/shopping/ShoppingCategorySection';
import { ShoppingItemRow } from '@/components/shopping/ShoppingItemRow';
import {
  ShoppingViewToggle,
  type ShoppingView,
} from '@/components/shopping/ShoppingViewToggle';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { copy } from '@/i18n/copy.it';
import { italianDateLong } from '@/lib/format';
import { createSyncChannel } from '@/lib/broadcastChannel';
import { cn } from '@/lib/cn';
import {
  composeTextExport,
  shoppingQueryKey,
  SHOPPING_CHANNEL,
  useResetShopping,
  useShopping,
  useToggleItem,
  type ShoppingItem,
  type ShoppingResponse,
} from '@/services/shopping';
import { useAuthStore } from '@/stores/auth';

/** Returns YYYY-MM-DD for the Monday of the current week (Europe/Rome local clock). */
function todayStartOfWeek(): string {
  return format(startOfWeek(new Date(), { weekStartsOn: 1 }), 'yyyy-MM-dd');
}

const MEAL_SLOT_COPY: Record<string, string> = {
  breakfast: copy.shopping.itemMealSlotBreakfast,
  lunch: copy.shopping.itemMealSlotLunch,
  dinner: copy.shopping.itemMealSlotDinner,
  snack: copy.shopping.itemMealSlotSnack,
};

const DAY_LONG_LABELS: string[] = [
  'lunedì',
  'martedì',
  'mercoledì',
  'giovedì',
  'venerdì',
  'sabato',
  'domenica',
];

/**
 * "Per giorno" view — group ItemRows by the day they contribute to. An item
 * with multiple ``sources`` shows under each contributing day so the user
 * sees the full daily picture (a 200 g pomodoro contributing to lunch + dinner
 * appears in both rows).
 */
function dayBucketsFromShopping(payload: ShoppingResponse): Array<{ day: number; items: Array<{ item: ShoppingItem; slot: string }> }> {
  const buckets: Array<{ day: number; items: Array<{ item: ShoppingItem; slot: string }> }> = [];
  for (let d = 0; d < 7; d++) {
    const dayItems: Array<{ item: ShoppingItem; slot: string }> = [];
    for (const cat of payload.categories) {
      for (const it of cat.items) {
        // sources are tagged like "lunch_d0", "dinner_d2"
        const matched = (it.sources ?? [])
          .filter((s) => s.endsWith(`_d${d}`))
          .map((s) => s.split('_')[0]);
        for (const slot of matched) {
          dayItems.push({ item: it, slot });
        }
      }
    }
    buckets.push({ day: d, items: dayItems });
  }
  return buckets;
}

function isAllEmpty(payload: ShoppingResponse): boolean {
  return payload.categories.every((c) => c.items.length === 0);
}

export default function Shopping(): React.ReactElement {
  const params = useParams<{ weekStart?: string }>();
  const userId = useAuthStore((s) => s.user?.id) ?? '';
  const qc = useQueryClient();

  // Resolve weekStart from URL or fall back to current Monday.
  const weekStart = params.weekStart ?? todayStartOfWeek();

  const { data, isLoading, isError, error } = useShopping(weekStart);
  const toggle = useToggleItem(weekStart);
  const reset = useResetShopping(weekStart);

  const [view, setView] = React.useState<ShoppingView>('category');
  const [resetOpen, setResetOpen] = React.useState(false);

  // Multi-tab sync (D-25): when another tab broadcasts a change, refetch.
  React.useEffect(() => {
    return createSyncChannel(SHOPPING_CHANNEL, () => {
      void qc.invalidateQueries({ queryKey: shoppingQueryKey(userId, weekStart) });
    });
  }, [userId, weekStart, qc]);

  const handleToggleItem = React.useCallback(
    (item: ShoppingItem, next: boolean) => {
      toggle.mutate({
        canonical_name: item.canonical_name,
        unit: item.unit,
        checked: next,
      });
    },
    [toggle],
  );

  const handleCopyText = React.useCallback(async () => {
    if (!data) return;
    try {
      await navigator.clipboard.writeText(composeTextExport(data));
      toast.success(copy.shopping.exportCopySuccess);
    } catch {
      toast.error(copy.errors.syncFailed);
    }
  }, [data]);

  const handleExportPdf = React.useCallback(() => {
    // Plan 02-06 wires this — for now surface the friendly message.
    toast.info(copy.shopping.exportPdfNotYet);
  }, []);

  const handleResetConfirm = React.useCallback(() => {
    setResetOpen(false);
    reset.mutate();
  }, [reset]);

  // ───── Loading state ─────
  if (isLoading) {
    return (
      <main className="px-[var(--spacing-4)] py-[var(--spacing-4)] flex flex-col gap-[var(--spacing-4)] max-w-[720px] mx-auto">
        <Skeleton className="h-[64px] w-full rounded-[var(--radius-card)]" />
        <Skeleton className="h-[120px] w-full rounded-[var(--radius-card)]" />
        <Skeleton className="h-[180px] w-full rounded-[var(--radius-card)]" />
      </main>
    );
  }

  // ───── No active plan / Empty state ─────
  if (isError) {
    const code = (error as { response?: { data?: { code?: string } } } | null)?.response?.data?.code;
    if (code === 'no_active_plan') {
      return <EmptyStateShopping />;
    }
    return (
      <main className="px-[var(--spacing-4)] py-[var(--spacing-4)] max-w-[720px] mx-auto">
        <p
          role="alert"
          className="text-[color:var(--color-text-muted)] text-center mt-[var(--spacing-8)]"
        >
          {copy.errors.generic500}
        </p>
      </main>
    );
  }

  if (!data || isAllEmpty(data)) {
    return <EmptyStateShopping />;
  }

  const weekStartDate = parseISO(weekStart);
  const subtitle = copy.shopping.subtitleFormat.replace(
    '{weekStartLong}',
    italianDateLong(weekStartDate),
  );

  return (
    <main
      className="px-[var(--spacing-4)] py-[var(--spacing-4)] flex flex-col gap-[var(--spacing-4)] max-w-[720px] mx-auto pb-[calc(96px+env(safe-area-inset-bottom))]"
      data-testid="shopping-page"
    >
      {/* ───── Header ───── */}
      <header className="flex flex-col gap-[var(--spacing-1)]">
        <h1 className="text-[length:var(--text-heading)] font-semibold m-0 text-[color:var(--color-text)]">
          {copy.shopping.heading}
        </h1>
        <p className="text-[color:var(--color-text-muted)] m-0">{subtitle}</p>
      </header>

      {/* ───── View toggle ───── */}
      <div>
        <ShoppingViewToggle value={view} onChange={setView} />
      </div>

      {/* ───── Body ───── */}
      {view === 'category' ? (
        <div className="flex flex-col gap-[var(--spacing-3)]">
          {data.categories.map((cat) => (
            <ShoppingCategorySection
              key={cat.name}
              name={cat.name}
              items={cat.items}
              onToggleItem={handleToggleItem}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col gap-[var(--spacing-3)]">
          {dayBucketsFromShopping(data).map(({ day, items }) => {
            // Reuse ShoppingCategorySection's collapse + header chrome but
            // pass each day as a "category" — caption builder shows the
            // contributing meal slot.
            const dayLabel = DAY_LONG_LABELS[day] ?? `giorno ${day + 1}`;
            const dayDate = addDays(weekStartDate, day);
            // Deduplicate items per day (an item can appear twice if both
            // lunch + dinner contribute) — show once with multi-slot caption.
            const seen = new Map<string, { item: ShoppingItem; slots: string[] }>();
            for (const { item, slot } of items) {
              const key = `${item.canonical_name}-${item.unit ?? 'none'}`;
              const ex = seen.get(key);
              if (ex) {
                if (!ex.slots.includes(slot)) ex.slots.push(slot);
              } else {
                seen.set(key, { item, slots: [slot] });
              }
            }
            const dedup = Array.from(seen.values());
            return (
              <details
                key={day}
                open
                className="rounded-[var(--radius-card)] border border-[color:var(--color-border)] bg-[color:var(--color-surface)]"
              >
                <summary
                  className={cn(
                    'list-none cursor-pointer select-none',
                    'flex items-baseline gap-[var(--spacing-3)]',
                    'min-h-11 px-[var(--spacing-4)] py-[var(--spacing-3)]',
                    'rounded-[var(--radius-card)]',
                  )}
                >
                  <h3 className="flex-1 m-0 font-semibold text-[length:var(--text-base)] text-[color:var(--color-text)] capitalize">
                    {dayLabel}
                  </h3>
                  <span className="font-mono text-[length:var(--text-caption)] text-[color:var(--color-text-muted)] tabular-nums">
                    {format(dayDate, 'dd/MM')}
                  </span>
                </summary>
                <div className="px-[var(--spacing-2)] pb-[var(--spacing-2)]">
                  {dedup.length === 0 ? (
                    <p className="text-[color:var(--color-text-muted)] px-[var(--spacing-3)] py-[var(--spacing-2)] m-0">
                      {copy.shopping.categoryEmpty}
                    </p>
                  ) : (
                    <ul className="list-none p-0 m-0 flex flex-col gap-[var(--spacing-1)]">
                      {dedup.map(({ item, slots }) => {
                        const slotLabels = slots.map((s) => MEAL_SLOT_COPY[s] ?? s.toUpperCase()).join(' · ');
                        return (
                          <ShoppingItemRowAdapter
                            key={`${item.canonical_name}-${item.unit ?? 'none'}`}
                            item={item}
                            caption={slotLabels}
                            onToggle={(next) => handleToggleItem(item, next)}
                          />
                        );
                      })}
                    </ul>
                  )}
                </div>
              </details>
            );
          })}
        </div>
      )}

      {/* ───── Sticky bottom action bar ───── */}
      <div
        className="fixed inset-x-0 bottom-0 z-20 border-t border-[color:var(--color-border)] bg-[color:var(--color-surface)]"
        style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
      >
        <div className="max-w-[720px] mx-auto px-[var(--spacing-4)] py-[var(--spacing-3)] flex flex-wrap items-center justify-between gap-[var(--spacing-2)]">
          <button
            type="button"
            onClick={() => setResetOpen(true)}
            className="inline-flex items-center gap-[var(--spacing-2)] min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)] text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text)] active:scale-[calc(1-0.03*var(--motion-scale))]"
          >
            <ArrowCounterClockwise size={18} weight="bold" aria-hidden="true" />
            {copy.shopping.resetCta}
          </button>
          <div className="flex items-center gap-[var(--spacing-2)]">
            <button
              type="button"
              onClick={() => void handleCopyText()}
              className="inline-flex items-center gap-[var(--spacing-2)] min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)] border border-[color:var(--color-border)] bg-[color:var(--color-surface)] text-[color:var(--color-text)] active:scale-[calc(1-0.03*var(--motion-scale))]"
            >
              <ClipboardText size={18} weight="regular" aria-hidden="true" />
              {copy.shopping.exportCopyCta}
            </button>
            <button
              type="button"
              onClick={handleExportPdf}
              className="inline-flex items-center gap-[var(--spacing-2)] min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)] bg-[color:var(--color-leaf-500)] text-[color:var(--color-text-inverse)] font-semibold shadow-[var(--shadow-1)] active:scale-[calc(1-0.03*var(--motion-scale))]"
            >
              <FilePdf size={18} weight="fill" aria-hidden="true" />
              {copy.shopping.exportPdfCta}
            </button>
          </div>
        </div>
      </div>

      {/* ───── Reset confirm dialog ───── */}
      <Dialog open={resetOpen} onOpenChange={setResetOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{copy.shopping.resetConfirmHeading}</DialogTitle>
            <DialogDescription>{copy.shopping.resetConfirmBody}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <button
              type="button"
              onClick={() => setResetOpen(false)}
              className="min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)] text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text)]"
            >
              {copy.shopping.resetConfirmCancel}
            </button>
            <button
              type="button"
              onClick={handleResetConfirm}
              className="min-h-11 px-[var(--spacing-4)] rounded-[var(--radius-pill)] bg-[color:var(--color-leaf-500)] text-[color:var(--color-text-inverse)] font-semibold"
            >
              {copy.shopping.resetConfirmCta}
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </main>
  );
}

// Internal adapter so the per-day view can pass a custom caption per slot.
function ShoppingItemRowAdapter({
  item,
  caption,
  onToggle,
}: {
  item: ShoppingItem;
  caption?: string;
  onToggle: (next: boolean) => void;
}): React.ReactElement {
  return <ShoppingItemRow item={item} contextCaption={caption} onToggle={onToggle} />;
}
