// frontend/src/components/auth/InviteSignupForm.tsx
// UI-SPEC §6.4 InviteSignupForm + §7.2 Italian copy lock.
//
// Behavior:
//   - Reads `?token=...` from the URL via useSearchParams.
//   - Missing token → render full-screen invite-invalid card (no form).
//   - Valid token → form (name, email, password, password-confirm) → POST /register.
//   - 400 token_expired → swap card to copy.invite.tokenExpired.
//   - 400 token_invalid → swap card to copy.invite.tokenInvalid.
//   - On success → navigate to /welcome (PersistStorageWelcome).
//
// Source: AUTH-09, AUTH-10, D-17, UI-SPEC §6.4 + §7.2.
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useSearchParams } from 'react-router';
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
import { registerWithInvite } from '@/services/auth';

const schema = z.object({
  username: z.string().min(2).max(50),
  email: z.string().email(),
  password: z.string().min(8),
});
type FormValues = z.infer<typeof schema>;

interface TokenErrorCardProps {
  heading: string;
}

function TokenErrorCard({ heading }: TokenErrorCardProps): React.ReactElement {
  return (
    <Card
      variant="raised"
      className="flex w-full max-w-md flex-col gap-[var(--spacing-4)] p-[var(--spacing-6)]"
    >
      <h1
        className="text-[length:var(--text-heading)] font-semibold text-[var(--color-text)]"
        role="alert"
      >
        {heading}
      </h1>
    </Card>
  );
}

export function InviteSignupForm(): React.ReactElement {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get('token') ?? '';
  const [submitting, setSubmitting] = useState(false);
  const [tokenError, setTokenError] = useState<'expired' | 'invalid' | null>(
    token ? null : 'invalid',
  );

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { username: '', email: '', password: '' },
  });

  async function onSubmit(values: FormValues): Promise<void> {
    setSubmitting(true);
    try {
      await registerWithInvite(token, values.email, values.username, values.password);
      navigate('/welcome', { replace: true });
    } catch (e) {
      const code = (e as ApiError | undefined)?.response?.data?.code;
      if (code === 'token_expired') {
        setTokenError('expired');
      } else if (code === 'token_invalid') {
        setTokenError('invalid');
      } else if (code === 'email_taken') {
        toast.error(
          (e as ApiError).response?.data?.detail ?? copy.errors.generic500,
        );
      } else {
        toast.error(copy.errors.generic500);
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (tokenError === 'expired') {
    return <TokenErrorCard heading={copy.invite.tokenExpired} />;
  }
  if (tokenError === 'invalid') {
    return <TokenErrorCard heading={copy.invite.tokenInvalid} />;
  }

  return (
    <Card variant="raised" className="w-full max-w-md p-[var(--spacing-6)]">
      <h1 className="mb-[var(--spacing-2)] text-[length:var(--text-heading)] font-semibold text-[var(--color-text)]">
        {copy.invite.heading}
      </h1>
      <p className="mb-[var(--spacing-6)] text-[length:var(--text-base)] text-[var(--color-text-muted)]">
        {copy.invite.subheading}
      </p>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-[var(--spacing-4)]"
          noValidate
        >
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{copy.invite.nameLabel}</FormLabel>
                <FormControl>
                  <Input type="text" autoComplete="name" {...field} />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.username ? copy.errors.generic500 : null}
                </FormMessage>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{copy.auth.emailLabel}</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    autoComplete="email"
                    inputMode="email"
                    placeholder={copy.auth.emailPlaceholder}
                    {...field}
                  />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.email ? copy.errors.generic500 : null}
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
                  <Input type="password" autoComplete="new-password" {...field} />
                </FormControl>
                <FormMessage>
                  {form.formState.errors.password ? copy.errors.generic500 : null}
                </FormMessage>
              </FormItem>
            )}
          />
          <Button type="submit" disabled={submitting} variant="primary">
            {copy.invite.submitCta}
          </Button>
        </form>
      </Form>
    </Card>
  );
}
