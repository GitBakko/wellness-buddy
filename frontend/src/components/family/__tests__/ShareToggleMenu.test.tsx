// frontend/src/components/family/__tests__/ShareToggleMenu.test.tsx
// Plan 02-07 — locks owner-only render + Switch state synchronisation.
// Radix DropdownMenu uses pointer events, not click events; userEvent.setup()
// dispatches the right event sequence in JSDOM.

import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { ShareToggleMenu } from '@/components/family/ShareToggleMenu';

const mutateMock = vi.fn();

// Mock `useShareToggle` so the component doesn't try to hit the network.
vi.mock('@/services/family', () => ({
  useShareToggle: () => ({ mutate: mutateMock, isPending: false }),
}));

describe('ShareToggleMenu (Plan 02-07)', () => {
  it('renders the trigger button with Italian aria-label', () => {
    mutateMock.mockClear();
    render(<ShareToggleMenu variantId="abc-123" currentVisibility="group_shared" />);
    const trigger = screen.getByTestId('share-toggle-trigger');
    expect(trigger).toBeInTheDocument();
    expect(trigger.getAttribute('aria-label')).toBe('Opzioni pasto');
  });

  it('opens the menu and exposes the Switch with Italian label', async () => {
    mutateMock.mockClear();
    const user = userEvent.setup();
    render(<ShareToggleMenu variantId="abc-123" currentVisibility="group_shared" />);
    await user.click(screen.getByTestId('share-toggle-trigger'));
    // Both the menu label and the Switch share the localised label
    const labels = await screen.findAllByText('Condividi con la famiglia');
    expect(labels.length).toBeGreaterThan(0);
  });

  it('initializes Switch state from currentVisibility=private (off)', async () => {
    mutateMock.mockClear();
    const user = userEvent.setup();
    render(<ShareToggleMenu variantId="abc-123" currentVisibility="private" />);
    await user.click(screen.getByTestId('share-toggle-trigger'));
    const sw = await screen.findByTestId('share-toggle-switch');
    // Radix Switch reflects state via aria-checked
    expect(sw.getAttribute('aria-checked')).toBe('false');
  });

  it('calls mutate with new visibility when Switch is toggled', async () => {
    mutateMock.mockClear();
    const user = userEvent.setup();
    render(<ShareToggleMenu variantId="abc-123" currentVisibility="private" />);
    await user.click(screen.getByTestId('share-toggle-trigger'));
    const sw = await screen.findByTestId('share-toggle-switch');
    await user.click(sw);
    expect(mutateMock).toHaveBeenCalledTimes(1);
    const [input] = mutateMock.mock.calls[0];
    expect(input).toEqual({ variantId: 'abc-123', visibility: 'group_shared' });
  });
});
