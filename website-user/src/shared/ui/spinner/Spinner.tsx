import { Loader2 } from 'lucide-react'

import { cn } from '@/shared/lib/cn'

import type { WithClassName } from '@/shared/types/ui'

export type SpinnerProps = WithClassName & {
  label?: string
}

export function Spinner({ className, label = 'Loading' }: SpinnerProps) {
  return (
    <div className={cn('inline-flex items-center gap-2 text-muted-foreground', className)}>
      <Loader2 className="h-5 w-5 animate-spin" aria-hidden />
      <span className="sr-only">{label}</span>
    </div>
  )
}
