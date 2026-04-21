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
    return <EmptyState title="尚無活動資料" description="後端填入 ops_activity_feed payload 後會顯示於此。" />
  }
  return <JsonPreview value={feed} />
}
