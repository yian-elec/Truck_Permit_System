import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { formatOperatorStage, formatOperatorStatus } from '@/shared/utils/admin-operator-copy'
import { formatDate } from '@/shared/utils/format-date'
import { Button, DataTable, type DataTableColumn, StatusBadge } from '@/shared/ui'

import type { EnrichedReviewTask } from './ReviewTaskListContent'

type Props = {
  tasks: EnrichedReviewTask[]
  onAssign: (applicationId: string) => void
}

function CellOrDash({
  loading,
  error,
  children,
}: {
  loading: boolean
  error: boolean
  children: ReactNode
}) {
  if (loading) return <span className="text-muted-foreground text-xs">載入中…</span>
  if (error) return <span className="text-muted-foreground text-xs">—</span>
  return <>{children}</>
}

export function ReviewTaskTable({ tasks, onAssign }: Props) {
  const columns: DataTableColumn<EnrichedReviewTask>[] = [
    {
      id: 'appno',
      header: '申請編號',
      cell: (r) => (
        <CellOrDash loading={r.case_loading} error={r.case_error}>
          <span className="font-medium text-foreground">{r.application_no}</span>
        </CellOrDash>
      ),
    },
    {
      id: 'applicant',
      header: '申請人',
      cell: (r) => (
        <CellOrDash loading={r.case_loading} error={r.case_error}>
          {r.applicant_name}
        </CellOrDash>
      ),
    },
    {
      id: 'plate',
      header: '車牌',
      cell: (r) => (
        <CellOrDash loading={r.case_loading} error={r.case_error}>
          <span className="tabular-nums">{r.plate}</span>
        </CellOrDash>
      ),
    },
    {
      id: 'period',
      header: '期間',
      cell: (r) => (
        <CellOrDash loading={r.case_loading} error={r.case_error}>
          {r.period_label}
        </CellOrDash>
      ),
    },
    {
      id: 'status',
      header: '狀態',
      cell: (r) => <StatusBadge status={formatOperatorStatus(r.status)} />,
    },
    {
      id: 'stage',
      header: '階段',
      cell: (r) => <span className="text-sm text-foreground">{formatOperatorStage(r.stage)}</span>,
    },
    {
      id: 'updated',
      header: '最後更新',
      cell: (r) => <span className="tabular-nums text-sm">{formatDate(r.updated_at)}</span>,
    },
    {
      id: 'actions',
      header: '操作',
      className: 'w-[1%] whitespace-nowrap',
      cell: (r) => (
        <div className="flex justify-end gap-2">
          <Button asChild variant="outline" size="sm">
            <Link to={routePaths.reviewCase(r.application_id)}>查看</Link>
          </Button>
          <Button type="button" variant="secondary" size="sm" onClick={() => onAssign(r.application_id)}>
            指派
          </Button>
        </div>
      ),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={tasks}
      getRowId={(r) => r.review_task_id}
      emptyMessage="沒有符合的申請，或關鍵字過濾後無結果。"
    />
  )
}
