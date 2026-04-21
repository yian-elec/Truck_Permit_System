import { Check } from 'lucide-react'

import { cn } from '@/shared/lib/cn'

export type StepperStep = {
  id: string
  label: string
}

export type StepperProps = {
  steps: StepperStep[]
  currentIndex: number
  className?: string
}

export function Stepper({ steps, currentIndex, className }: StepperProps) {
  return (
    <ol className={cn('flex flex-wrap gap-2', className)}>
      {steps.map((step, i) => {
        const done = i < currentIndex
        const active = i === currentIndex
        return (
          <li
            key={step.id}
            className={cn(
              'flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs font-medium',
              done && 'border-primary/40 bg-primary/5 text-primary',
              active && 'border-primary bg-primary/10 text-primary',
              !done && !active && 'border-border text-muted-foreground',
            )}
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full border border-current text-[10px]">
              {done ? <Check className="h-3 w-3" /> : i + 1}
            </span>
            {step.label}
          </li>
        )
      })}
    </ol>
  )
}
