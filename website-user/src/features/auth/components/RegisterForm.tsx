import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { Link, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

import { ApiError } from '@/shared/api/api-error'
import { routePaths } from '@/shared/constants/route-paths'
import { getSafeReturnPath, withReturnQuery } from '@/features/auth/lib/safe-return-url'
import { Button, Form, FormField, Input } from '@/shared/ui'

import { useRegister } from '../hooks/useRegister'
import { type RegisterFormValues, registerFormSchema } from '../validators/register-form.schema'

type Props = {
  onRegistered?: () => void
}

export function RegisterForm({ onRegistered }: Props) {
  const [searchParams] = useSearchParams()
  const returnPath = getSafeReturnPath(searchParams.get('returnUrl'))
  const loginTo = withReturnQuery(routePaths.login, returnPath)
  const register = useRegister()
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerFormSchema),
    defaultValues: {
      display_name: '',
      email: '',
      mobile: '',
      password: '',
    },
  })

  const onSubmit = (values: RegisterFormValues) => {
    register.mutate(values, {
      onSuccess: () => {
        toast.success('註冊成功，請登入')
        onRegistered?.()
      },
      onError: (error) => {
        const err = ApiError.fromUnknown(error)
        form.setError('root', { message: err.message })
      },
    })
  }

  return (
    <FormProvider {...form}>
      <Form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField<RegisterFormValues>
          name="display_name"
          label="顯示名稱"
          children={(field) => (
            <Input
              id="display_name"
              autoComplete="name"
              name={field.name}
              ref={field.ref as React.Ref<HTMLInputElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
            />
          )}
        />
        <FormField<RegisterFormValues>
          name="email"
          label="電子郵件"
          children={(field) => (
            <Input
              id="email"
              type="email"
              autoComplete="email"
              name={field.name}
              ref={field.ref as React.Ref<HTMLInputElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
            />
          )}
        />
        <FormField<RegisterFormValues>
          name="mobile"
          label="手機"
          children={(field) => (
            <Input
              id="mobile"
              type="tel"
              autoComplete="tel"
              name={field.name}
              ref={field.ref as React.Ref<HTMLInputElement>}
              value={String(field.value ?? '')}
              onBlur={field.onBlur}
              onChange={field.onChange}
            />
          )}
        />
        <FormField<RegisterFormValues>
          name="password"
          label="密碼"
          children={(field) => (
            <Input
              id="password"
              type="password"
              autoComplete="new-password"
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
        <Button type="submit" className="w-full" loading={register.isPending}>
          建立帳戶
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          已有帳號？{' '}
          <Link className="text-primary underline-offset-4 hover:underline" to={loginTo}>
            登入
          </Link>
        </p>
      </Form>
    </FormProvider>
  )
}
