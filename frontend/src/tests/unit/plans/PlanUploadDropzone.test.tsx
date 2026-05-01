// frontend/src/tests/unit/plans/PlanUploadDropzone.test.tsx
// Plan 04 Task 3: PlanUploadDropzone variant rendering tests.
//
// State machine: idle | dragging | parsing | error | preview (UI-SPEC §6.4).

import { describe, expect, it, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import { PlanUploadDropzone } from '@/components/plans/PlanUploadDropzone';
import { copy } from '@/i18n/copy.it';

describe('PlanUploadDropzone (UI-SPEC §6.4)', () => {
  it('renders idle variant with italian copy by default', () => {
    render(<PlanUploadDropzone onUploaded={vi.fn()} />);
    expect(screen.getByText(copy.plans.dropzoneIdle)).toBeInTheDocument();
  });

  it('renders file input with .md accept attribute', () => {
    render(<PlanUploadDropzone onUploaded={vi.fn()} />);
    const fileInput = screen.getByLabelText(copy.plans.dropzoneIdle, {
      selector: 'input[type="file"]',
    });
    expect(fileInput).toHaveAttribute('accept', '.md,text/markdown');
  });

  it('shows dragging variant on dragenter', () => {
    const { container } = render(<PlanUploadDropzone onUploaded={vi.fn()} />);
    const dropzone = container.querySelector('[data-testid="plan-dropzone"]');
    expect(dropzone).not.toBeNull();
    if (dropzone) {
      fireEvent.dragEnter(dropzone, { dataTransfer: { types: ['Files'] } });
      expect(screen.getByText(copy.plans.dropzoneDragging)).toBeInTheDocument();
    }
  });

  it('reverts to idle on dragleave', () => {
    const { container } = render(<PlanUploadDropzone onUploaded={vi.fn()} />);
    const dropzone = container.querySelector('[data-testid="plan-dropzone"]');
    if (dropzone) {
      fireEvent.dragEnter(dropzone, { dataTransfer: { types: ['Files'] } });
      fireEvent.dragLeave(dropzone);
      expect(screen.getByText(copy.plans.dropzoneIdle)).toBeInTheDocument();
    }
  });

  it('shows error variant with role=alert when upload fails', async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Solo file .md sono supportati.', code: 'bad_file_type' }),
    } as Response);
    globalThis.fetch = fetchSpy;

    const { container } = render(<PlanUploadDropzone onUploaded={vi.fn()} />);
    const fileInput = container.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    const file = new File(['x'], 'plan.txt', { type: 'text/plain' });
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);

    await waitFor(() => {
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      expect(alert.textContent).toContain('.md');
    });
  });
});
