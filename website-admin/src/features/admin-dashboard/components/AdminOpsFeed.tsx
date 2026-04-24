import { EmptyState } from '@/shared/ui'
import { JsonPreview } from '@/shared/ui'

type Props = {
  loading?: boolean
  feed?: Record<string, unknown>
}

export function AdminOpsFeed({ loading, feed }: Props) {
  if (loading) {
    return <div className="bg-muted/40 h-32 animate-pulse rounded-md" />
  }
  if (!feed || Object.keys(feed).length === 0) {
    return <EmptyState title="尚無活動資料" description="目前尚無最近活動紀錄。" />
  }
  return <JsonPreview value={feed} />
}
