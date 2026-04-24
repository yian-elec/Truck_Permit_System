import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import { ApiError } from '@/shared/api/api-error'
import { Button, Form, FormField, Input } from '@/shared/ui'

import { useLogin } from '../hooks/useLogin'
import { type LoginFormValues, loginFormSchema } from '../validators/login-form.schema'

export function LoginForm() {
  const login = useLogin()
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = (values: LoginFormValues) => {
    login.mutate(values, {
      onError: (error) => {
        const err = ApiError.fromUnknown(error)
        form.setError('root', { message: err.message })
      },
    })
  }

  return (
    <FormProvider {...form}>
      <Form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField<LoginFormValues>
          name="email"
          label="帳號 / Email"
          children={(field) => (
            <Input
              id="email"
              type="text"
              autoComplete="username"
              placeholder="請輸入帳號或 Email"
              name={field.name}
              ref={field.ref as React.Ref<HTMLInputElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
            />
          )}
        />
        <FormField<LoginFormValues>
          name="password"
          label="密碼"
          children={(field) => (
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder="請輸入密碼"
              name={field.name}
              ref={field.ref as React.Ref<HTMLInputElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
            />
          )}
        />
        {form.formState.errors.root?.message ? (
          <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive" role="alert">
            {String(form.formState.errors.root.message)}
          </p>
        ) : null}
        <Button type="submit" className="w-full" loading={login.isPending}>
          登入
        </Button>
      </Form>
    </FormProvider>
  )
}
