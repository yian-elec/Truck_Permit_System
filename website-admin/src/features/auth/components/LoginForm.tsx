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
          label="Email or username"
          children={(field) => (
            <Input
              id="email"
              type="text"
              autoComplete="username"
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
          label="Password"
          children={(field) => (
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
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
        <Button type="submit" className="w-full" loading={login.isPending}>
          Sign in
        </Button>
      </Form>
    </FormProvider>
  )
}
