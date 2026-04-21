import { cn } from '@/shared/lib/cn'

import type { WithChildren, WithClassName } from '@/shared/types/ui'

export type PageContainerProps = WithChildren &
  WithClassName & {
    as?: 'div' | 'main' | 'section'
  }

export function PageContainer({ as: Comp = 'div', className, children }: PageContainerProps) {
  return (
    <Comp className={cn('mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 lg:px-8', className)}>
      {children}
    </Comp>
  )
}
