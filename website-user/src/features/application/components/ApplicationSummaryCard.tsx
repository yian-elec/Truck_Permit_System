import { formatApplicationStatus } from '@/shared/utils/format-application-status'
import { formatDate } from '@/shared/utils/format-date'
import { StatusBadge } from '@/shared/ui'

import type { ApplicationDetailDto } from '../api/get-application-detail'

export function ApplicationSummaryCard({ detail }: { detail: ApplicationDetailDto }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border p-4">
      <div>
        <p className="text-sm text-muted-foreground">案件</p>
        <p className="text-lg font-semibold">{detail.application_no}</p>
        <p className="text-xs text-muted-foreground">更新於 {formatDate(detail.updated_at)}</p>
      </div>
      <StatusBadge>{formatApplicationStatus(detail.status)}</StatusBadge>
    </div>
  )
}
