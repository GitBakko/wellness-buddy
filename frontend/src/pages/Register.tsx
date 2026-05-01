// frontend/src/pages/Register.tsx
// Plan 03 — invite-token signup page wrapper.
import { InviteSignupForm } from '@/components/auth/InviteSignupForm';

export default function Register(): React.ReactElement {
  return (
    <main className="flex min-h-dvh items-center justify-center p-[var(--spacing-4)]">
      <InviteSignupForm />
    </main>
  );
}
