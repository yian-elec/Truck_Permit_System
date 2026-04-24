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
    <div className="border-border bg-background/95 sticky bottom-0 z-10 border-t backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-2 px-4 py-3 sm:px-6 lg:px-8">
        {/* 次要操作 */}
        <Button type="button" variant="ghost" size="sm" onClick={onComment}>
          新增評論
        </Button>
        <Button asChild variant="outline" size="sm">
          <Link to={routePaths.reviewRoute(applicationId)}>路線審查</Link>
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={onSupplement}>
          補件要求
        </Button>
        {/* 分隔 */}
        <div className="flex-1" />
        {/* 主要決策 */}
        <Button type="button" variant="destructive" size="sm" onClick={onReject}>
          駁回
        </Button>
        <Button type="button" variant="default" size="sm" onClick={onApprove}>
          ✓ 核准
        </Button>
      </div>
    </div>
  )
}
