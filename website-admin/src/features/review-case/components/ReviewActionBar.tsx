import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { Button } from '@/shared/ui'

type Props = {
  applicationId: string
  onSupplement: () => void
  onApprove: () => void
  onReject: () => void
  onComment: () => void
}

export function ReviewActionBar({
  applicationId,
  onSupplement,
  onApprove,
  onReject,
  onComment,
}: Props) {
  return (
    <div className="border-border bg-card/50 sticky bottom-0 z-10 flex flex-wrap gap-2 border-t py-4">
      <Button type="button" variant="outline" size="sm" onClick={onSupplement}>
        補件
      </Button>
      <Button type="button" variant="default" size="sm" onClick={onApprove}>
        核准
      </Button>
      <Button type="button" variant="destructive" size="sm" onClick={onReject}>
        駁回
      </Button>
      <Button asChild variant="secondary" size="sm">
        <Link to={routePaths.reviewRoute(applicationId)}>前往路線審查</Link>
      </Button>
      <Button type="button" variant="ghost" size="sm" onClick={onComment}>
        新增評論
      </Button>
    </div>
  )
}
