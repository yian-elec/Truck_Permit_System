import { cn } from '@/shared/lib/cn'

export function JsonPreview({ value, className }: { value: unknown; className?: string }) {
  const text = JSON.stringify(value, null, 2)
  return (
    <pre
      className={cn(
        'bg-muted/50 text-muted-foreground max-h-96 overflow-auto rounded-md border border-border p-3 text-xs leading-relaxed',
        className,
      )}
    >
      {text}
    </pre>
  )
}
