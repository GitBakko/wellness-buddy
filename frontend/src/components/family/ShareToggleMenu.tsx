// frontend/src/components/family/ShareToggleMenu.tsx
// Plan 02-07 — DotsThreeOutline → DropdownMenu → Switch toggling visibility.
//
// Shown ONLY when:
//   - meal.owner_user_id === current_user_id (caller IS the owner)
//   - meal.variant_id is set (a WeeklyPlanVariant row exists; the toggle
//     mutates THAT row's visibility column)
//
// Anatomy (UI-SPEC §6.2):
//   ⊙⊙⊙ ←  44×44 button, Phosphor DotsThreeOutline 24px
//   └─ DropdownMenu opens on click
//      ┌──────────────────────────────────┐
//      │ 👥  Condividi con la famiglia [⚪] │  ← Switch toggles inline
//      └──────────────────────────────────┘
//
// Optimistic update: we flip the local Switch state instantly; on mutation
// success the toast confirms; on error (incl. 409) the parent's onError
// handler restores previous state via `useShareToggle`.
//
// Tap-scale 0.97/80ms (UI-13). All tokens (CLAUDE.md UI rule 1).

import { useState } from 'react';

import { DotsThreeOutline, UsersThree } from '@/components/icons';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Switch } from '@/components/ui/switch';
import { copy } from '@/i18n/copy.it';
import { useShareToggle } from '@/services/family';

interface ShareToggleMenuProps {
  variantId: string;
  currentVisibility: 'private' | 'group_shared';
  /** Optional — when provided, success path invalidates the matching weekly query. */
  weekStart?: string;
}

export function ShareToggleMenu({
  variantId,
  currentVisibility,
  weekStart,
}: ShareToggleMenuProps): React.ReactElement {
  const [isShared, setIsShared] = useState(currentVisibility === 'group_shared');
  const toggle = useShareToggle(weekStart);

  const handleToggle = (next: boolean) => {
    setIsShared(next);
    toggle.mutate(
      { variantId, visibility: next ? 'group_shared' : 'private' },
      {
        // Roll back local state on failure so the Switch matches reality.
        onError: () => setIsShared(!next),
      },
    );
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label={copy.family.sharePerMealMenuAria}
          data-testid="share-toggle-trigger"
          className="inline-flex items-center justify-center w-11 h-11 rounded-[var(--radius-md)] text-[color:var(--color-text-muted)] hover:bg-[var(--color-surface-muted)] hover:text-[color:var(--color-text)] transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--color-leaf-500)]"
        >
          <DotsThreeOutline size={22} weight="regular" aria-hidden="true" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" sideOffset={6} className="min-w-[260px]">
        <DropdownMenuItem
          onSelect={(e) => e.preventDefault()}
          className="flex items-center gap-[var(--spacing-3)] py-[var(--spacing-3)] px-[var(--spacing-3)] min-h-11"
        >
          <UsersThree
            size={18}
            weight="regular"
            aria-hidden="true"
            className="text-[color:var(--color-text-muted)] flex-shrink-0"
          />
          <span className="flex-1 text-[var(--text-base)] font-medium text-[color:var(--color-text)]">
            {copy.family.sharePerMealToggleLabel}
          </span>
          <Switch
            checked={isShared}
            onCheckedChange={handleToggle}
            disabled={toggle.isPending}
            aria-label={copy.family.sharePerMealToggleLabel}
            data-testid="share-toggle-switch"
          />
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
