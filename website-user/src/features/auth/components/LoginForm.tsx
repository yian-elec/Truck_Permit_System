import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'

import { ApiError } from '@/shared/api/api-error'
import { routePaths } from '@/shared/constants/route-paths'
import { Button, Form, FormField, Input } from '@/shared/ui'

import { useLogin } from '../hooks/useLogin'
import { type LoginFormValues, loginFormSchema } from '../validators/login-form.schema'

export function LoginForm() {
  const login = useLogin()
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: { identifier: '', password: '' },
  })

  const onSubmit = (values: LoginFormValues) => {
    login.mutate(
      {
        login_mode: 'password',
        identifier: values.identifier,
        password: values.password,
      },
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
        <FormField<LoginFormValues>
          name="identifier"
          label="電子郵件或帳號"
          children={(field) => (
            <Input
              id="identifier"
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
          label="密碼"
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
          登入
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          還沒有帳號？{' '}
          <Link className="text-primary underline-offset-4 hover:underline" to={routePaths.register}>
            前往註冊
          </Link>
        </p>
      </Form>
    </FormProvider>
  )
}
