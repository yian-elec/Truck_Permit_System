import { zodResolver } from '@hookform/resolvers/zod'
import type { Ref } from 'react'
import { useMemo } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { Link, useLocation } from 'react-router-dom'
import { z } from 'zod'

import { routePaths } from '@/shared/constants/route-paths'
import { storageKeys } from '@/shared/constants/storage-keys'
import { ApiError } from '@/shared/api/api-error'
import { Button, Form, FormField, Input } from '@/shared/ui'

import { useMfaVerify } from '../hooks/useMfaVerify'

const schema = z.object({
  code: z.string().min(4, '至少 4 碼').max(32),
})

type FormValues = z.infer<typeof schema>

export function MfaPage() {
  const location = useLocation()
  const mfa = useMfaVerify()

  const challengeId = useMemo(() => {
    const fromNav = (location.state as { challengeId?: string | null } | null)?.challengeId
    if (fromNav) return fromNav
    try {
      return sessionStorage.getItem(storageKeys.mfaChallengeId)
    } catch {
      return null
    }
  }, [location.state])

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { code: '' },
  })

  if (!challengeId) {
    return (
      <div className="mx-auto max-w-md space-y-4 p-6">
        <h1 className="text-xl font-semibold">無法驗證 MFA</h1>
        <p className="text-muted-foreground text-sm">缺少 challenge，請重新登入。</p>
        <Button asChild variant="default">
          <Link to={routePaths.login}>返回登入</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-md space-y-6 p-6">
      <div>
        <h1 className="text-xl font-semibold">二階段驗證</h1>
        <p className="text-muted-foreground mt-1 text-sm">請輸入驗證應用程式或簡訊提供的一次性密碼。</p>
      </div>
      <FormProvider {...form}>
        <Form
          onSubmit={form.handleSubmit((values) =>
            mfa.mutate(
              { challenge_id: challengeId, code: values.code },
              {
                onError: (err) => {
                  const e = ApiError.fromUnknown(err)
                  form.setError('root', { message: e.message })
                },
              },
            ),
          )}
          className="space-y-4"
        >
          <FormField<FormValues>
            name="code"
            label="驗證碼"
            children={(field) => (
              <Input
                id="code"
                name={field.name}
                ref={field.ref as Ref<HTMLInputElement>}
                value={String(field.value ?? '')}
                onBlur={field.onBlur}
                onChange={field.onChange}
                autoComplete="one-time-code"
                inputMode="numeric"
              />
            )}
          />
          {form.formState.errors.root?.message ? (
            <p className="text-destructive text-sm" role="alert">
              {String(form.formState.errors.root.message)}
            </p>
          ) : null}
          <Button type="submit" className="w-full" loading={mfa.isPending}>
            驗證並登入
          </Button>
        </Form>
      </FormProvider>
      <p className="text-center">
        <Link to={routePaths.login} className="text-muted-foreground text-sm underline">
          返回登入
        </Link>
      </p>
    </div>
  )
}
