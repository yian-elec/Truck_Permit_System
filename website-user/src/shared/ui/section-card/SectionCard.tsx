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
        'rounded-xl border border-border bg-background shadow-sm',
        className,
      )}
    >
      {title ? (
        <div className="border-b border-border px-5 py-4 sm:px-6">
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          {description ? <p className="mt-0.5 text-sm text-muted-foreground">{description}</p> : null}
        </div>
      ) : null}
      <div className="p-5 sm:p-6">{children}</div>
    </section>
  )
}
