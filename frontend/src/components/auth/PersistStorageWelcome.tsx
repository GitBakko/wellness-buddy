// frontend/src/components/auth/PersistStorageWelcome.tsx
// D-15, FND-08 — first-login welcome screen that requests `navigator.storage.persist()`.
//
// UX flow (UI-SPEC §6.4 PersistStorageWelcome):
//   - Heading: "Benvenuto in Wellness Buddy"
//   - Body: short italian explanation of why persistence matters
//   - Primary CTA: "Abilita storage offline" → calls requestPersistentStorage,
//     then navigates to /today
//   - Secondary CTA: "Più tardi" → skips, navigates to /today (toast on denial
//     comes from persistStorage helper if user later opts in via Settings)
//
// Italian copy NOT routed through `copy.it.ts` for the welcome heading/body
// because Plan 05b's locked copy table doesn't yet include welcome strings;
// adding them would require touching copy.it.ts which is owned by Plan 05b.
// This is a deliberate scope boundary — when copy.it.ts gains a `welcome`
// section, swap to `copy.welcome.heading` etc.
import { useNavigate } from 'react-router';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { requestPersistentStorage } from '@/lib/persistStorage';

export function PersistStorageWelcome(): React.ReactElement {
  const navigate = useNavigate();

  async function onAccept(): Promise<void> {
    const granted = await requestPersistentStorage();
    // Persist decision so future logins skip the welcome screen.
    localStorage.setItem('wb:persist-decision', granted ? 'granted' : 'denied');
    navigate('/today', { replace: true });
  }

  function onSkip(): void {
    localStorage.setItem('wb:persist-decision', 'skipped');
    navigate('/today', { replace: true });
  }

  return (
    <main className="flex min-h-dvh items-center justify-center p-[var(--spacing-6)]">
      <Card
        variant="raised"
        className="flex w-full max-w-md flex-col gap-[var(--spacing-6)] p-[var(--spacing-6)]"
      >
        <h1 className="text-[length:var(--text-heading)] font-semibold text-[var(--color-text)]">
          Benvenuto in Wellness Buddy
        </h1>
        <p className="text-[length:var(--text-base)] text-[var(--color-text-muted)]">
          Abilita lo storage offline per continuare a usare l&apos;app anche senza connessione.
        </p>
        <div className="flex flex-col gap-[var(--spacing-3)]">
          <Button onClick={onAccept} type="button" variant="primary">
            Abilita storage offline
          </Button>
          <Button onClick={onSkip} type="button" variant="ghost">
            Più tardi
          </Button>
        </div>
      </Card>
    </main>
  );
}
