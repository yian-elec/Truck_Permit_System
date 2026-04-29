import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { isTerminalApplicationStatus } from '@/shared/utils/admin-operator-copy'
import { Button } from '@/shared/ui'

type Props = {
  applicationId: string
  /** 來自案件的 `application.status`，用於終局狀態時隱藏核准／駁回／補件 */
  applicationStatus?: string | null
  onSupplement: () => void
  onApprove: () => void
  onReject: () => void
  onComment: () => void
}

export function ReviewActionBar({
  applicationId,
  applicationStatus,
  onSupplement,
  onApprove,
  onReject,
  onComment,
}: Props) {
  const decisionLocked = isTerminalApplicationStatus(applicationStatus)

  return (
    <div className="border-border bg-background/95 sticky bottom-0 z-10 border-t backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-2 px-4 py-3 sm:px-6 lg:px-8">
        <Button type="button" variant="ghost" size="sm" onClick={onComment}>
          新增評論
        </Button>
        <Button asChild variant="outline" size="sm">
          <Link to={routePaths.reviewRoute(applicationId)}>路線審查</Link>
        </Button>
        {!decisionLocked ? (
          <>
            <Button type="button" variant="outline" size="sm" onClick={onSupplement}>
              補件要求
            </Button>
            <div className="flex-1" />
            <Button type="button" variant="destructive" size="sm" onClick={onReject}>
              駁回
            </Button>
            <Button type="button" variant="default" size="sm" onClick={onApprove}>
              ✓ 核准
            </Button>
          </>
        ) : (
          <>
            <div className="flex-1" />
            <p className="text-muted-foreground max-w-md text-right text-xs sm:text-sm">
              本案已結案或已定案，無法再次核准、駁回或要求補件。
            </p>
          </>
        )}
      </div>
    </div>
  )
}
