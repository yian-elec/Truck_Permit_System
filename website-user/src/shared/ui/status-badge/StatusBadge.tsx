import { cva, type VariantProps } from 'class-variance-authority'
import type { ReactNode } from 'react'

import { cn } from '@/shared/lib/cn'

import type { WithClassName } from '@/shared/types/ui'

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium',
  {
    variants: {
      variant: {
        default: 'border-border bg-muted text-foreground',
        success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
        warning: 'border-amber-500/30 bg-amber-500/10 text-amber-800 dark:text-amber-400',
        destructive: 'border-destructive/30 bg-destructive/10 text-destructive',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

export type StatusBadgeProps = WithClassName &
  VariantProps<typeof badgeVariants> & {
    children: ReactNode
  }

export function StatusBadge({ className, variant, children }: StatusBadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)}>{children}</span>
}
