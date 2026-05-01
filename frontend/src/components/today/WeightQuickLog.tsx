// frontend/src/components/today/WeightQuickLog.tsx
// UI-SPEC §6.4 + §7.2 — Italian decimal input ("75,3"), token-only colors.
//
// Pitfall #9 mitigation: parseItalianDecimal accepts both `,` and `.`; out-of-range
// values surface a `role="alert"` italian message (UI-15).
//
// CONV-12: server is canonical (Decimal precision 2). Frontend rounds to 2 decimals
// before posting.

import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { copy } from '@/i18n/copy.it';
import { italianNumber, parseItalianDecimal } from '@/lib/format';
import { useLogWeight } from '@/services/weight';

/** Subset shape — matches both `WeightLog` (full row) and `TodayWeight` (today aggregator). */
interface ExistingWeight {
  id: string;
  weight_kg: number;
}

interface Props {
  /** Today's weight if already logged — pre-fills + flips the toast copy to "aggiornato". */
  existing?: ExistingWeight | null;
  /** Override today's date (testing). Defaults to ISO YYYY-MM-DD in user's local tz. */
  todayIso?: string;
}

function defaultTodayIso(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

const ERROR_INVALID = 'Inserisci un peso valido (es. 75,3).';

export function WeightQuickLog({ existing, todayIso }: Props): React.ReactElement {
  const log = useLogWeight();
  const [value, setValue] = useState<string>(
    existing ? italianNumber(existing.weight_kg) : '',
  );
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    setError(null);
    const parsed = parseItalianDecimal(value);
    if (Number.isNaN(parsed) || parsed < 30 || parsed > 250) {
      setError(ERROR_INVALID);
      return;
    }
    const rounded = Math.round(parsed * 100) / 100; // 2-decimal precision
    const date = todayIso ?? defaultTodayIso();
    try {
      await log.mutateAsync({ date, weight_kg: rounded });
      toast.success(existing ? copy.weight.editToast : copy.weight.successToast);
    } catch {
      toast.error(copy.errors.generic500);
    }
  }

  return (
    <Card
      className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-3)]"
      aria-label={copy.weight.heading}
    >
      <h2 className="text-[var(--text-base)] font-semibold text-[color:var(--color-text)]">
        {copy.weight.heading}
      </h2>
      <form
        onSubmit={onSubmit}
        className="flex flex-wrap items-end gap-[var(--spacing-3)]"
        noValidate
      >
        <div className="flex flex-col flex-1 min-w-[160px] gap-[var(--spacing-1)]">
          <Label htmlFor="weight-quick-log-input">{copy.weight.inputLabel}</Label>
          <Input
            id="weight-quick-log-input"
            inputMode="decimal"
            value={value}
            placeholder="75,3"
            autoComplete="off"
            onChange={(e) => {
              setValue(e.target.value);
              if (error) setError(null);
            }}
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? 'weight-quick-log-error' : undefined}
          />
          {error && (
            <p
              id="weight-quick-log-error"
              role="alert"
              className="inline-flex items-center gap-[var(--spacing-1)] text-[var(--text-caption)] text-[color:var(--color-destructive)]"
            >
              <AlertCircle size={14} aria-hidden="true" />
              {error}
            </p>
          )}
        </div>
        <Button type="submit" disabled={log.isPending}>
          {copy.weight.submitCta}
        </Button>
      </form>
    </Card>
  );
}
