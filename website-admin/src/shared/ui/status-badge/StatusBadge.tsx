import { cn } from '@/shared/lib/cn'

const toneMap: Record<string, string> = {
  pending: 'bg-amber-500/15 text-amber-900 dark:text-amber-100',
  in_review: 'bg-blue-500/15 text-blue-900 dark:text-blue-100',
  approved: 'bg-emerald-500/15 text-emerald-900 dark:text-emerald-100',
  rejected: 'bg-red-500/15 text-red-900 dark:text-red-100',
  active: 'bg-emerald-500/15 text-emerald-900 dark:text-emerald-100',
  inactive: 'bg-muted text-muted-foreground',
  /** 與 active／inactive 同色，供中文標籤使用 */
  已啟用: 'bg-emerald-500/15 text-emerald-900 dark:text-emerald-100',
  未啟用: 'bg-muted text-muted-foreground',
  success: 'bg-emerald-500/15 text-emerald-900 dark:text-emerald-100',
  failed: 'bg-red-500/15 text-red-900 dark:text-red-100',
  running: 'bg-blue-500/15 text-blue-900 dark:text-blue-100',
}

export function StatusBadge({
  status,
  className,
}: {
  status: string
  className?: string
}) {
  const key = status.toLowerCase().replace(/\s+/g, '_')
  const tone = toneMap[key] ?? 'bg-muted text-foreground'
  return (
    <span
      className={cn(
        'inline-flex max-w-full items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        tone,
        className,
      )}
    >
      {status}
    </span>
  )
}
