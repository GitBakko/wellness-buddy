// frontend/src/pages/Login.tsx
// Plan 03 — login page wrapper. Composes LoginForm in a centered viewport layout.
import { LoginForm } from '@/components/auth/LoginForm';

export default function Login(): React.ReactElement {
  return (
    <main className="flex min-h-dvh items-center justify-center p-[var(--spacing-4)]">
      <LoginForm />
    </main>
  );
}
