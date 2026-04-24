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
  /** 操作者語意狀態（與 formatOperatorStatus 一致） */
  等待處理: 'bg-amber-500/15 text-amber-900 dark:text-amber-100',
  審核中: 'bg-blue-500/15 text-blue-900 dark:text-blue-100',
  已核准: 'bg-emerald-500/15 text-emerald-900 dark:text-emerald-100',
  已駁回: 'bg-red-500/15 text-red-900 dark:text-red-100',
  已送出: 'bg-sky-500/15 text-sky-900 dark:text-sky-100',
  已結案: 'bg-muted text-foreground',
  已完成: 'bg-emerald-500/15 text-emerald-900 dark:text-emerald-100',
  失敗需處理: 'bg-red-500/15 text-red-900 dark:text-red-100',
  處理中: 'bg-blue-500/15 text-blue-900 dark:text-blue-100',
  草稿: 'bg-muted text-muted-foreground',
  已取消: 'bg-muted text-muted-foreground',
  新進件: 'bg-amber-500/15 text-amber-900 dark:text-amber-100',
  補件中: 'bg-amber-500/15 text-amber-900 dark:text-amber-100',
  使用中: 'bg-emerald-500/15 text-emerald-900 dark:text-emerald-100',
  未使用: 'bg-muted text-muted-foreground',
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
