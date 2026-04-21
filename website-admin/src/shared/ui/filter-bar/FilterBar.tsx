import type { ReactNode } from 'react'

import { cn } from '@/shared/lib/cn'

export function FilterBar({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        'border-border bg-muted/20 flex flex-wrap items-end gap-3 rounded-md border p-3',
        className,
      )}
    >
      {children}
    </div>
  )
}
