import type { ReactNode } from 'react'

import { cn } from '@/shared/lib/cn'

type InfoRowProps = {
  label: string
  children: ReactNode
  className?: string
}

export function InfoRow({ label, children, className }: InfoRowProps) {
  return (
    <div className={cn('grid gap-1 sm:grid-cols-[minmax(8rem,12rem)_1fr] sm:items-start', className)}>
      <dt className="text-muted-foreground text-sm font-medium">{label}</dt>
      <dd className="text-sm">{children}</dd>
    </div>
  )
}
