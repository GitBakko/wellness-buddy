// frontend/src/components/plans/PlanUploadDropzone.tsx
// Plan 04 Task 3 — drag&drop file uploader with 5 variants
// (idle | dragging | parsing | error | preview) per UI-SPEC §6.4.
//
// All copy from `copy.plans.*` (FND-09). All colors via @theme tokens (UI-01).
// Errors carry `role="alert"` + icon + italian copy + token color (UI-15).
// Touch targets ≥44px (UI-06). prefers-reduced-motion honored via --motion-scale (UI-05).

import * as React from 'react';
import { CircleAlert, FileText, Loader, Upload } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { copy } from '@/i18n/copy.it';
import { cn } from '@/lib/cn';
import { uploadPlan, type PlanUploadResponse } from '@/services/plans';

type DropzoneState =
  | { kind: 'idle' }
  | { kind: 'dragging' }
  | { kind: 'parsing' }
  | { kind: 'error'; message: string }
  | { kind: 'preview'; uploaded: PlanUploadResponse };

interface PlanUploadDropzoneProps {
  onUploaded?: (resp: PlanUploadResponse) => void;
}

function isMarkdownFile(file: File): boolean {
  const lower = file.name.toLowerCase();
  return lower.endsWith('.md') || file.type === 'text/markdown';
}

function mapErrorCode(code: string | undefined): string {
  switch (code) {
    case 'bad_file_type':
      return copy.plans.errorBadFileType;
    case 'too_large':
      return copy.plans.errorTooLarge;
    case 'parse_failed':
      return copy.plans.errorParseFailed;
    default:
      return copy.plans.errorGenericUpload;
  }
}

export function PlanUploadDropzone({
  onUploaded,
}: PlanUploadDropzoneProps): React.ReactElement {
  const [state, setState] = React.useState<DropzoneState>({ kind: 'idle' });
  const [planName, setPlanName] = React.useState<string>('');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleFile = React.useCallback(
    async (file: File): Promise<void> => {
      if (!isMarkdownFile(file)) {
        setState({ kind: 'error', message: copy.plans.errorBadFileType });
        return;
      }

      setState({ kind: 'parsing' });
      const fallbackName = planName.trim() || file.name.replace(/\.md$/i, '');
      try {
        const resp = await uploadPlan(file, fallbackName);
        setState({ kind: 'preview', uploaded: resp });
        onUploaded?.(resp);
      } catch (err) {
        const code = (err as { response?: { data?: { code?: string } } })?.response
          ?.data?.code;
        setState({ kind: 'error', message: mapErrorCode(code) });
      }
    },
    [onUploaded, planName],
  );

  const onDragOver = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    if (state.kind !== 'dragging' && state.kind !== 'parsing') {
      setState({ kind: 'dragging' });
    }
  };

  const onDragEnter = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    if (state.kind === 'idle' || state.kind === 'error') {
      setState({ kind: 'dragging' });
    }
  };

  const onDragLeave = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    if (state.kind === 'dragging') {
      setState({ kind: 'idle' });
    }
  };

  const onDrop = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    const file = e.dataTransfer?.files?.[0];
    if (file) {
      void handleFile(file);
    } else {
      setState({ kind: 'idle' });
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files?.[0];
    if (file) {
      void handleFile(file);
    }
  };

  const reset = (): void => {
    setState({ kind: 'idle' });
    setPlanName('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <Card
      variant="flat"
      className="flex flex-col gap-[var(--spacing-4)] p-[var(--spacing-4)] sm:p-[var(--spacing-6)]"
    >
      <div className="flex flex-col gap-[var(--spacing-2)]">
        <Label htmlFor="plan-name-input" className="text-[length:var(--text-base)]">
          {copy.plans.nameLabel}
        </Label>
        <Input
          id="plan-name-input"
          type="text"
          placeholder={copy.plans.namePlaceholder}
          value={planName}
          onChange={(e) => setPlanName(e.target.value)}
        />
      </div>

      <div
        data-testid="plan-dropzone"
        data-state={state.kind}
        onDragOver={onDragOver}
        onDragEnter={onDragEnter}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={cn(
          'flex min-h-[160px] flex-col items-center justify-center gap-[var(--spacing-3)]',
          'rounded-[var(--radius-card)] border-2 border-dashed',
          'p-[var(--spacing-6)] text-center',
          'transition-colors duration-[var(--duration-fast)] ease-[var(--ease-out-soft)]',
          state.kind === 'dragging'
            ? 'border-[var(--color-coral-500)] bg-[var(--color-surface-muted)]'
            : 'border-[var(--color-border)] bg-[var(--color-surface)]',
        )}
      >
        {state.kind === 'idle' && (
          <>
            <Upload
              className="size-8 text-[var(--color-text-muted)]"
              aria-hidden="true"
            />
            <Label
              htmlFor="plan-file-input"
              className="cursor-pointer text-[length:var(--text-base)] text-[var(--color-text)]"
            >
              {copy.plans.dropzoneIdle}
            </Label>
            <Input
              ref={fileInputRef}
              id="plan-file-input"
              type="file"
              accept=".md,text/markdown"
              aria-label={copy.plans.dropzoneIdle}
              className="sr-only"
              onChange={onFileChange}
            />
          </>
        )}

        {state.kind === 'dragging' && (
          <>
            <Upload
              className="size-8 text-[var(--color-coral-500)]"
              aria-hidden="true"
            />
            <p className="text-[length:var(--text-base)] font-medium text-[var(--color-coral-700)]">
              {copy.plans.dropzoneDragging}
            </p>
            <Input
              ref={fileInputRef}
              id="plan-file-input"
              type="file"
              accept=".md,text/markdown"
              aria-label={copy.plans.dropzoneIdle}
              className="sr-only"
              onChange={onFileChange}
            />
          </>
        )}

        {state.kind === 'parsing' && (
          <>
            <Loader
              className="size-8 animate-spin text-[var(--color-text-muted)]"
              style={
                {
                  animationDuration: 'calc(1000ms * var(--motion-scale, 1))',
                } as React.CSSProperties
              }
              aria-hidden="true"
            />
            <p className="text-[length:var(--text-base)] text-[var(--color-text-muted)]">
              {copy.plans.parsingState}
            </p>
          </>
        )}

        {state.kind === 'error' && (
          <>
            <CircleAlert
              className="size-8 text-[var(--color-destructive)]"
              aria-hidden="true"
            />
            <p
              role="alert"
              className="text-[length:var(--text-base)] text-[var(--color-destructive)]"
            >
              {state.message}
            </p>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={reset}
            >
              {copy.plans.cancelCta}
            </Button>
            <Input
              ref={fileInputRef}
              id="plan-file-input"
              type="file"
              accept=".md,text/markdown"
              aria-label={copy.plans.dropzoneIdle}
              className="sr-only"
              onChange={onFileChange}
            />
          </>
        )}

        {state.kind === 'preview' && (
          <>
            <FileText
              className="size-8 text-[var(--color-success)]"
              aria-hidden="true"
            />
            <p className="text-[length:var(--text-base)] font-medium text-[var(--color-text)]">
              {state.uploaded.name}
            </p>
            {state.uploaded.unrecognized_headings.length > 0 && (
              <div
                role="status"
                className="rounded-[var(--radius-md)] bg-[var(--color-warning-bg)] p-[var(--spacing-3)] text-[length:var(--text-caption)] text-[var(--color-text)]"
              >
                <p className="font-semibold">{copy.plans.parseWarningsHeading}</p>
                <p>
                  {copy.plans.parseWarningsBody.replace(
                    '{list}',
                    state.uploaded.unrecognized_headings.join(', '),
                  )}
                </p>
              </div>
            )}
            <Button type="button" variant="ghost" size="sm" onClick={reset}>
              {copy.plans.cancelCta}
            </Button>
          </>
        )}
      </div>
    </Card>
  );
}
