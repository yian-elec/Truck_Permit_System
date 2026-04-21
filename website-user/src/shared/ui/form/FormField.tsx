import type { ReactNode } from 'react'
import { Controller, useFormContext, type FieldPath, type FieldValues } from 'react-hook-form'

import { cn } from '@/shared/lib/cn'

import type { WithClassName } from '@/shared/types/ui'

export type FormFieldProps<T extends FieldValues> = WithClassName & {
  name: FieldPath<T>
  label: string
  /** 為 true 時於標籤後顯示紅色 *（必填） */
  required?: boolean
  description?: string
  children: (args: {
    value: unknown
    onChange: (...event: unknown[]) => void
    onBlur: () => void
    name: string
    ref: React.Ref<unknown>
  }) => ReactNode
}

export function FormField<T extends FieldValues>({
  name,
  label,
  required,
  description,
  className,
  children,
}: FormFieldProps<T>) {
  const {
    control,
    formState: { errors },
  } = useFormContext<T>()

  const message = errors[name]?.message

  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium leading-none" htmlFor={String(name)}>
        {label}
        {required ? <span className="text-destructive"> *</span> : null}
      </label>
      {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
      <Controller
        name={name}
        control={control}
        render={({ field }) => <>{children(field)}</>}
      />
      {message ? <p className="text-sm text-destructive">{String(message)}</p> : null}
    </div>
  )
}
