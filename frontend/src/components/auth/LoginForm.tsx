// frontend/src/components/auth/LoginForm.tsx
// UI-SPEC §6.4 LoginForm + §7.2 Italian copy lock + UI-16 iOS keyboard.
//
// Behavior:
//   - email + password fields, react-hook-form + zod, italian-only copy
//   - autoComplete="username" + "current-password" so password managers + iOS
//     autofill work (UI-16)
//   - On invalid_credentials → toast.error with `copy.auth.invalidCreds`
//   - On expired/no_token → `copy.auth.sessionExpired`
//   - Errors rendered with role="alert" + icon (FormMessage primitive UI-15)
//   - Touch microinteraction (scale 0.97 80ms) inherited from Button primitive
//
// Source: AUTH-01..AUTH-12, UI-SPEC §6.4 + §7.2, UI-15, UI-16.
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { copy } from '@/i18n/copy.it';
import type { ApiError } from '@/services/api';
import { login } from '@/services/auth';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});
type FormValues = z.infer<typeof schema>;

export function LoginForm(): React.ReactElement {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '' },
  });

  async function onSubmit(values: FormValues): Promise<void> {
    setSubmitting(true);
    try {
      await login(values.email, values.password);
      // Plan 02-07 follow-up — show /welcome only on FIRST login. Returning
      // users skip straight to /today; clearing localStorage resets it.
      const decision = localStorage.getItem('wb:persist-decision');
      navigate(decision ? '/today' : '/welcome', { replace: true });
    } catch (e) {
      const code = (e as ApiError | undefined)?.response?.data?.code;
      const message =
        code === 'invalid_credentials'
          ? copy.auth.invalidCreds
          : code === 'no_token' || code === 'expired'
            ? copy.auth.sessionExpired
            : copy.errors.generic500;
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card variant="raised" className="w-full max-w-md p-[var(--spacing-6)]">
      <h1 className="mb-[var(--spacing-6)] text-[length:var(--text-heading)] font-semibold text-[var(--color-text)]">
        {copy.auth.loginHeading}
      </h1>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-[var(--spacing-4)]"
          noValidate
        >
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{copy.auth.emailLabel}</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    autoComplete="username"
                    inputMode="email"
                    placeholder={copy.auth.emailPlaceholder}
                    {...field}
                  />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.email ? copy.auth.invalidCreds : null}
                </FormMessage>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{copy.auth.passwordLabel}</FormLabel>
                <FormControl>
                  <Input type="password" autoComplete="current-password" {...field} />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.password ? copy.auth.invalidCreds : null}
                </FormMessage>
              </FormItem>
            )}
          />
          <Button type="submit" disabled={submitting} variant="primary">
            {copy.auth.submitCta}
          </Button>
        </form>
      </Form>
    </Card>
  );
}
