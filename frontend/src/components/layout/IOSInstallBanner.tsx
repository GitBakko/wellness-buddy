// frontend/src/components/layout/IOSInstallBanner.tsx
// D-16 + UI-SPEC §10.1 — iOS Safari install banner.
//
// Trigger rules:
//   - User is on iOS Safari (not Chrome/Firefox/Edge for iOS)
//   - PWA is NOT already in standalone display-mode (already installed)
//   - This is at least the 2nd visit (D-16 — avoid blocking first impression)
//   - User has not dismissed within last 7 days
//
// Dismissed state persisted in localStorage (key: wb-install-banner-dismissed-until).
// Visit count persisted in localStorage (key: wb-visit-count).

import { useEffect, useState } from 'react';
import { copy } from '@/i18n/copy.it';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTitle } from '@/components/ui/sheet';

const DISMISS_KEY = 'wb-install-banner-dismissed-until';
const VISIT_KEY = 'wb-visit-count';
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

function isIOSSafari(): boolean {
  if (typeof navigator === 'undefined') return false;
  const ua = navigator.userAgent;
  return /iP(hone|od|ad)/.test(ua) && /Safari/.test(ua) && !/CriOS|FxiOS|EdgiOS/.test(ua);
}

function isStandalone(): boolean {
  if (typeof window === 'undefined') return false;
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true
  );
}

/** Compute initial open state synchronously so we never call setState in
 *  useEffect (React 19 guidance + react-hooks/set-state-in-effect). The
 *  visit-count side-effect (write to localStorage) lives in a separate
 *  effect that does not touch React state. */
function shouldOpenInstallBanner(): boolean {
  if (typeof window === 'undefined') return false;
  if (!isIOSSafari() || isStandalone()) return false;
  const dismissedUntil = Number(localStorage.getItem(DISMISS_KEY) ?? 0);
  if (Date.now() < dismissedUntil) return false;
  const visits = Number(localStorage.getItem(VISIT_KEY) ?? 0) + 1;
  return visits >= 2;
}

export function IOSInstallBanner() {
  const [open, setOpen] = useState<boolean>(() => shouldOpenInstallBanner());

  // Side-effect only: bump visit count in localStorage. No setState here.
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!isIOSSafari() || isStandalone()) return;
    const visits = Number(localStorage.getItem(VISIT_KEY) ?? 0) + 1;
    localStorage.setItem(VISIT_KEY, String(visits));
  }, []);

  function dismiss() {
    localStorage.setItem(DISMISS_KEY, String(Date.now() + SEVEN_DAYS_MS));
    setOpen(false);
  }

  if (!open) return null;
  return (
    <Sheet open={open} onOpenChange={(o) => !o && dismiss()}>
      <SheetContent
        side="bottom"
        className="p-[var(--spacing-6)] flex flex-col gap-[var(--spacing-4)]"
      >
        <SheetTitle className="text-[var(--text-heading)]">
          {copy.pwa.installHeading}
        </SheetTitle>
        <p className="text-[color:var(--color-text-muted)]">
          {copy.pwa.installBody}
        </p>
        <ol className="flex flex-col gap-[var(--spacing-2)] list-decimal pl-[var(--spacing-6)]">
          <li>{copy.pwa.installStep1}</li>
          <li>{copy.pwa.installStep2}</li>
          <li>{copy.pwa.installStep3}</li>
        </ol>
        <Button variant="ghost" onClick={dismiss}>
          {copy.pwa.installDismiss}
        </Button>
      </SheetContent>
    </Sheet>
  );
}
