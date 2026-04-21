import * as React from 'react'
import { ChevronDown } from 'lucide-react'

import { cn } from '@/shared/lib/cn'

import type { WithClassName } from '@/shared/types/ui'

import type { SelectProps } from './select.types'

export const Select = React.forwardRef<HTMLSelectElement, SelectProps & WithClassName>(
  ({ className, options, placeholder, disabled, id, ...props }, ref) => {
    return (
      <div className="relative w-full">
        <select
          id={id}
          ref={ref}
          disabled={disabled}
          className={cn(
            'flex h-9 w-full appearance-none rounded-md border border-input bg-background py-1 pl-3 pr-9 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
            className,
          )}
          {...props}
        >
          {placeholder ? (
            <option value="" disabled>
              {placeholder}
            </option>
          ) : null}
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown
          className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden
        />
      </div>
    )
  },
)
Select.displayName = 'Select'
