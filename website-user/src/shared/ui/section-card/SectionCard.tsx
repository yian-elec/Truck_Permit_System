import { cn } from '@/shared/lib/cn'

import type { WithChildren, WithClassName } from '@/shared/types/ui'

export type SectionCardProps = WithChildren &
  WithClassName & {
    title?: string
    description?: string
  }

export function SectionCard({ title, description, className, children }: SectionCardProps) {
  return (
    <section
      className={cn(
        'rounded-lg border border-border bg-background p-4 shadow-sm sm:p-6',
        className,
      )}
    >
      {title ? (
        <div className="mb-4 space-y-1">
          <h2 className="text-lg font-semibold leading-none">{title}</h2>
          {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
        </div>
      ) : null}
      {children}
    </section>
  )
}
