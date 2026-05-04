// frontend/src/pages/Plans.tsx
// Plan 04 Task 3 — /piano page composition.
//
// Layout (mobile-first):
//   1. Page heading
//   2. PlanUploadDropzone — drag/drop or file picker → on success populates `pending`
//   3. Pending preview (if any): unrecognized-headings warning + diff vs active + activate/cancel
//   4. List of past uploads with active badge
//   5. Confirm dialog before activation
//
// All copy from copy.plans.* (FND-09). All colors via @theme tokens (UI-01).
// Italian dates via Intl.DateTimeFormat('it-IT') (UI-18).

import * as React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogTitle,
} from '@/components/ui/dialog';
import { PlanDiffView } from '@/components/plans/PlanDiffView';
import { PlanUploadDropzone } from '@/components/plans/PlanUploadDropzone';
import { copy } from '@/i18n/copy.it';
import {
  activatePlan,
  diffPlan,
  listPlans,
  type PlanDiffResponse,
  type PlanListItem,
  type PlanUploadResponse,
} from '@/services/plans';

const ITALIAN_DATE_FORMAT = new Intl.DateTimeFormat('it-IT', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
});

function formatUploadedAt(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return ITALIAN_DATE_FORMAT.format(d);
}

export default function Plans(): React.ReactElement {
  const qc = useQueryClient();
  const { data: plans = [] } = useQuery<PlanListItem[]>({
    queryKey: ['plans'],
    queryFn: listPlans,
  });

  const [pending, setPending] = React.useState<PlanUploadResponse | null>(null);
  const [diff, setDiff] = React.useState<PlanDiffResponse | null>(null);
  const [confirming, setConfirming] = React.useState<string | null>(null);

  const activate = useMutation({
    mutationFn: (planId: string) => activatePlan(planId),
    onSuccess: () => {
      toast.success(copy.plans.activateSuccess);
      void qc.invalidateQueries({ queryKey: ['plans'] });
      setConfirming(null);
      setPending(null);
      setDiff(null);
    },
    onError: () => {
      toast.error(copy.plans.activateFailed);
    },
  });

  const handleUploaded = React.useCallback(async (resp: PlanUploadResponse) => {
    setPending(resp);
    void qc.invalidateQueries({ queryKey: ['plans'] });
    try {
      const result = await diffPlan(resp.id);
      setDiff(result);
    } catch {
      // Diff is best-effort — first plan with no active baseline returns
      // a 200 with all-added; only network/auth failures land here. Skip silently.
      setDiff(null);
    }
  }, [qc]);

  return (
    <main className="flex flex-col gap-[var(--spacing-6)] p-[var(--spacing-4)] sm:p-[var(--spacing-6)] mx-auto max-w-3xl">
      <h1 className="text-[length:var(--text-display)] font-semibold leading-[var(--leading-display)] text-[var(--color-text)]">
        {copy.plans.heading}
      </h1>

      <PlanUploadDropzone onUploaded={(r) => void handleUploaded(r)} />

      {pending && (
        <section className="flex flex-col gap-[var(--spacing-4)]">
          {diff && <PlanDiffView diff={diff} />}
          <div className="flex flex-row gap-[var(--spacing-3)]">
            <Button
              type="button"
              variant="primary"
              onClick={() => setConfirming(pending.id)}
              disabled={activate.isPending}
            >
              {copy.plans.activateCta}
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setPending(null);
                setDiff(null);
              }}
            >
              {copy.plans.cancelCta}
            </Button>
          </div>
        </section>
      )}

      <section className="flex flex-col gap-[var(--spacing-3)]">
        <h2 className="text-[length:var(--text-heading)] font-semibold leading-[var(--leading-heading)] text-[var(--color-text)]">
          {copy.plans.listHeading}
        </h2>
        {plans.length === 0 ? (
          <p className="text-[length:var(--text-base)] text-[var(--color-text-muted)]">
            {copy.plans.listEmpty}
          </p>
        ) : (
          <ul className="flex flex-col gap-[var(--spacing-2)]">
            {plans.map((p) => (
              <li
                key={p.id}
                className="flex flex-row items-center justify-between gap-[var(--spacing-3)] rounded-[var(--radius-card)] border border-[var(--color-border)] bg-[var(--color-bg-elev)] p-[var(--spacing-3)] sm:p-[var(--spacing-4)]"
              >
                <span className="flex flex-col gap-[var(--spacing-1)] min-w-0">
                  <span className="truncate text-[length:var(--text-base)] font-medium text-[var(--color-text)]">
                    {p.name}
                    {p.is_active && (
                      <span className="ml-[var(--spacing-2)] text-[length:var(--text-caption)] font-semibold text-[var(--color-coral-700)]">
                        ({copy.plans.listActiveBadge})
                      </span>
                    )}
                  </span>
                  <span className="text-[length:var(--text-caption)] text-[var(--color-text-muted)]">
                    {formatUploadedAt(p.uploaded_at)}
                  </span>
                </span>
                {!p.is_active && (
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => setConfirming(p.id)}
                    disabled={activate.isPending}
                  >
                    {copy.plans.activateCta}
                  </Button>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <Dialog
        open={confirming !== null}
        onOpenChange={(open) => {
          if (!open) setConfirming(null);
        }}
      >
        <DialogContent>
          <DialogTitle>{copy.plans.activateCta}</DialogTitle>
          <DialogDescription>
            {diff && !diff.has_active_plan
              ? copy.plans.activateConfirmFirst
              : copy.plans.activateConfirm}
          </DialogDescription>
          <DialogFooter className="mt-[var(--spacing-4)] flex flex-row gap-[var(--spacing-3)]">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setConfirming(null)}
              disabled={activate.isPending}
            >
              {copy.plans.cancelCta}
            </Button>
            <Button
              type="button"
              variant="primary"
              onClick={() => confirming && activate.mutate(confirming)}
              disabled={activate.isPending}
            >
              {copy.plans.activateCta}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </main>
  );
}
