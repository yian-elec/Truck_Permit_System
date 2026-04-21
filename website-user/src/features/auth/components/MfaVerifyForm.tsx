import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { useEffect } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import { ApiError } from '@/shared/api/api-error'
import { Button, Form, FormField, Input } from '@/shared/ui'

import { useVerifyMfa } from '../hooks/useVerifyMfa'
import { useAuthStore } from '../store/auth.store'
import { type MfaFormValues, mfaFormSchema } from '../validators/mfa-form.schema'

export function MfaVerifyForm() {
  const challenge = useAuthStore((s) => s.mfaChallenge)
  const verify = useVerifyMfa()
  const form = useForm<MfaFormValues>({
    resolver: zodResolver(mfaFormSchema),
    defaultValues: { challenge_id: challenge?.challenge_id ?? '', code: '' },
  })

  useEffect(() => {
    if (challenge?.challenge_id) {
      form.setValue('challenge_id', challenge.challenge_id)
    }
  }, [challenge?.challenge_id, form])

  const onSubmit = (values: MfaFormValues) => {
    verify.mutate(
      { challenge_id: values.challenge_id, code: values.code },
      {
        onError: (error) => {
          const err = ApiError.fromUnknown(error)
          form.setError('root', { message: err.message })
        },
      },
    )
  }

  return (
    <FormProvider {...form}>
      <Form onSubmit={form.handleSubmit(onSubmit)}>
        <input type="hidden" {...form.register('challenge_id')} />
        <FormField<MfaFormValues>
          name="code"
          label="一次性驗證碼"
          description="請輸入驗證器 App 顯示的 6 位數代碼。"
          children={(field) => (
            <Input
              id="code"
              inputMode="numeric"
              autoComplete="one-time-code"
              name={field.name}
              ref={field.ref as React.Ref<HTMLInputElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
            />
          )}
        />
        {form.formState.errors.root?.message ? (
          <p className="text-sm text-destructive" role="alert">
            {String(form.formState.errors.root.message)}
          </p>
        ) : null}
        <Button type="submit" className="w-full" loading={verify.isPending}>
          驗證
        </Button>
      </Form>
    </FormProvider>
  )
}
