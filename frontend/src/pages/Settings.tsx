// frontend/src/pages/Settings.tsx
// Phase 1 /impostazioni — theme picker (light/dark/system) + locked Italian
// language note + logout. All copy from copy.it.ts (FND-09); colors via tokens.

import { useNavigate } from 'react-router';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { copy } from '@/i18n/copy.it';
import { logout } from '@/services/auth';
import { useThemeStore, type ThemeMode } from '@/stores/theme';

const THEME_OPTIONS: Array<{ mode: ThemeMode; label: string }> = [
  { mode: 'light', label: copy.settings.themeLight },
  { mode: 'dark', label: copy.settings.themeDark },
  { mode: 'system', label: copy.settings.themeSystem },
];

export default function Settings(): React.ReactElement {
  const mode = useThemeStore((s) => s.mode);
  const setMode = useThemeStore((s) => s.setMode);
  const navigate = useNavigate();

  async function onLogout(): Promise<void> {
    try {
      await logout();
      toast.success(copy.auth.logoutToast);
    } finally {
      navigate('/login', { replace: true });
    }
  }

  return (
    <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-4)] max-w-2xl mx-auto">
      <h1 className="text-[var(--text-display)] font-semibold text-[color:var(--color-text)]">
        {copy.appBar.settings}
      </h1>

      {/* Theme picker */}
      <Card className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-3)]">
        <h2 className="text-[var(--text-heading)] font-semibold text-[color:var(--color-text)]">
          {copy.settings.themeHeading}
        </h2>
        <div className="flex flex-wrap gap-[var(--spacing-2)]" role="radiogroup" aria-label={copy.settings.themeHeading}>
          {THEME_OPTIONS.map(({ mode: m, label }) => (
            <Button
              key={m}
              type="button"
              variant={mode === m ? 'primary' : 'outline'}
              role="radio"
              aria-checked={mode === m}
              onClick={() => setMode(m)}
            >
              {label}
            </Button>
          ))}
        </div>
      </Card>

      {/* Language locked Italian (Phase 1) */}
      <Card className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-2)]">
        <h2 className="text-[var(--text-heading)] font-semibold text-[color:var(--color-text)]">
          {copy.settings.languageHeading}
        </h2>
        <p className="text-[color:var(--color-text)]">{copy.settings.languageValue}</p>
        <p className="text-[var(--text-caption)] text-[color:var(--color-text-muted)]">
          {copy.settings.languageNote}
        </p>
      </Card>

      {/* Logout */}
      <Card className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-3)]">
        <h2 className="text-[var(--text-heading)] font-semibold text-[color:var(--color-text)]">
          {copy.auth.logoutCta}
        </h2>
        <Button variant="destructive" onClick={() => void onLogout()} className="self-start">
          {copy.settings.logoutCta}
        </Button>
      </Card>
    </main>
  );
}
