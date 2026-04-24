import type { ReactNode } from 'react'

import { cn } from '@/shared/lib/cn'

type SectionCardProps = {
  title?: string
  description?: string
  actions?: ReactNode
  children: ReactNode
  className?: string
}

export function SectionCard({ title, description, actions, children, className }: SectionCardProps) {
  return (
    <section
      className={cn(
        'rounded-xl border border-border bg-background shadow-sm',
        className,
      )}
    >
      {(title || actions) ? (
        <div className="flex flex-wrap items-start justify-between gap-2 border-b border-border px-5 py-4 sm:px-6">
          {title ? (
            <div>
              <h2 className="text-base font-semibold text-foreground leading-tight">{title}</h2>
              {description ? <p className="mt-0.5 text-sm text-muted-foreground">{description}</p> : null}
            </div>
          ) : null}
          {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
        </div>
      ) : null}
      <div className="p-5 sm:p-6">{children}</div>
    </section>
  )
}
