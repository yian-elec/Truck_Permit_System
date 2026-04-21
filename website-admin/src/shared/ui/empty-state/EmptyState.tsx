import type { LucideIcon } from 'lucide-react'

import { cn } from '@/shared/lib/cn'

import type { WithChildren, WithClassName } from '@/shared/types/ui'

export type EmptyStateProps = WithChildren &
  WithClassName & {
    icon?: LucideIcon
    title: string
    description?: string
  }

export function EmptyState({ icon: Icon, title, description, className, children }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border p-8 text-center',
        className,
      )}
    >
      {Icon ? <Icon className="h-10 w-10 text-muted-foreground" aria-hidden /> : null}
      <div className="space-y-1">
        <h3 className="text-lg font-medium">{title}</h3>
        {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {children}
    </div>
  )
}
