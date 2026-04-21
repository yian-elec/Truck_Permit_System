import type { FormHTMLAttributes } from 'react'

import { cn } from '@/shared/lib/cn'

import type { WithClassName } from '@/shared/types/ui'

export type FormProps = FormHTMLAttributes<HTMLFormElement> & WithClassName

export function Form({ className, ...props }: FormProps) {
  return <form className={cn('space-y-4', className)} noValidate {...props} />
}
