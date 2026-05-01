// frontend/src/components/ai/__tests__/AIWidget.test.tsx
// T-AI-01 verification — Phase 1 AIWidget renders ONLY static italian copy from
// copy.it.ts. No data interpolation, no network calls, no user context leakage.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { AIWidget } from '@/components/ai/AIWidget';
import { copy } from '@/i18n/copy.it';

describe('AIWidget (T-AI-01 Phase 1 placeholder)', () => {
  it('renders italian heading from copy.ai.placeholderHeading', () => {
    render(<AIWidget />);
    expect(screen.getByText(copy.ai.placeholderHeading)).toBeInTheDocument();
  });

  it('renders italian body from copy.ai.placeholderBody', () => {
    render(<AIWidget />);
    expect(screen.getByText(copy.ai.placeholderBody)).toBeInTheDocument();
  });

  it('does not render any user data (T-AI-01 mitigation)', () => {
    // Render with a fake username in the auth store would still be safe — the widget
    // never imports useAuthStore. Spot check by verifying nothing matches an email.
    const { container } = render(<AIWidget />);
    expect(container.innerHTML).not.toMatch(/@/);
    expect(container.innerHTML).not.toMatch(/user/i);
  });

  it('region role is set so screen readers announce it', () => {
    render(<AIWidget />);
    const region = screen.getByRole('region', {
      name: copy.ai.placeholderHeading,
    });
    expect(region).toBeInTheDocument();
  });
});
