// frontend/src/components/weight/WeightHistoryTable.tsx
// Phase 1 simple history list — each row a Card with date + value + edit/delete.
// Italian date formatting; row actions confirm via window.confirm (Phase 1 simple).
// Dialog-based confirm comes Phase 2 alongside variant editor.

import { useState } from 'react';
import { Pencil, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { copy } from '@/i18n/copy.it';
import { italianDateLong, italianNumber, parseItalianDecimal } from '@/lib/format';
import {
  useDeleteWeight,
  useUpdateWeight,
  useWeights,
  type WeightLog,
} from '@/services/weight';

function EditRow({
  row,
  onDone,
}: {
  row: WeightLog;
  onDone: () => void;
}): React.ReactElement {
  const update = useUpdateWeight();
  const [value, setValue] = useState<string>(italianNumber(row.weight_kg));

  async function onSave(): Promise<void> {
    const n = parseItalianDecimal(value);
    if (Number.isNaN(n) || n < 30 || n > 250) {
      toast.error('Inserisci un peso valido (es. 75,3).');
      return;
    }
    try {
      await update.mutateAsync({
        id: row.id,
        weight_kg: Math.round(n * 100) / 100,
        date: row.date,
      });
      toast.success(copy.weight.editToast);
      onDone();
    } catch {
      toast.error(copy.errors.generic500);
    }
  }

  return (
    <div className="flex items-center gap-[var(--spacing-2)] flex-1">
      <Input
        inputMode="decimal"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        aria-label={copy.weight.inputLabel}
        className="max-w-[120px]"
      />
      <Button size="sm" onClick={onSave} disabled={update.isPending}>
        {copy.weight.submitCta}
      </Button>
      <Button size="sm" variant="ghost" onClick={onDone} type="button">
        {copy.plans.cancelCta}
      </Button>
    </div>
  );
}

export function WeightHistoryTable(): React.ReactElement {
  const { data, isLoading } = useWeights();
  const del = useDeleteWeight();
  const [editingId, setEditingId] = useState<string | null>(null);

  async function onDelete(row: WeightLog): Promise<void> {
    const confirmMsg = copy.weight.deleteConfirm.replace(
      '{data}',
      italianDateLong(new Date(row.date)),
    );
    if (!window.confirm(confirmMsg)) return;
    try {
      await del.mutateAsync(row.id);
      toast.success(copy.weight.deleteSuccess);
    } catch {
      toast.error(copy.errors.generic500);
    }
  }

  if (isLoading) {
    return <p className="text-[color:var(--color-text-muted)]">…</p>;
  }
  if (!data || data.length === 0) {
    return (
      <p className="text-[color:var(--color-text-muted)]">
        {copy.today.emptyDayBlank.body}
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-[var(--spacing-2)]" aria-label="Storico pesate">
      {data.map((row) => (
        <li key={row.id}>
          <Card className="p-[var(--spacing-3)] flex items-center justify-between gap-[var(--spacing-3)]">
            <div className="flex flex-col">
              <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] capitalize">
                {italianDateLong(new Date(row.date))}
              </span>
              {editingId === row.id ? (
                <EditRow row={row} onDone={() => setEditingId(null)} />
              ) : (
                <span className="font-mono tabular-nums text-[var(--text-base)] text-[color:var(--color-text)]">
                  {italianNumber(row.weight_kg)} kg
                </span>
              )}
            </div>
            {editingId !== row.id && (
              <div className="flex gap-[var(--spacing-1)]">
                <Button
                  size="icon"
                  variant="ghost"
                  aria-label="Modifica"
                  onClick={() => setEditingId(row.id)}
                >
                  <Pencil aria-hidden="true" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  aria-label={copy.weight.deleteCta}
                  onClick={() => void onDelete(row)}
                >
                  <Trash2 aria-hidden="true" />
                </Button>
              </div>
            )}
          </Card>
        </li>
      ))}
    </ul>
  );
}
