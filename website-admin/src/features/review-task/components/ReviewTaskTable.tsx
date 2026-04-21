import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { formatDate } from '@/shared/utils/format-date'
import { Button, DataTable, type DataTableColumn, StatusBadge } from '@/shared/ui'

import type { ReviewTaskSummary } from '../api/review-task-api'

type Props = {
  tasks: ReviewTaskSummary[]
  onAssign: (applicationId: string) => void
}

export function ReviewTaskTable({ tasks, onAssign }: Props) {
  const columns: DataTableColumn<ReviewTaskSummary>[] = [
    { id: 'task', header: '任務 ID', cell: (r) => <span className="font-mono text-xs">{r.review_task_id}</span> },
    {
      id: 'app',
      header: '案件 ID',
      cell: (r) => <span className="font-mono text-xs">{r.application_id}</span>,
    },
    { id: 'stage', header: '階段', cell: (r) => r.stage },
    {
      id: 'status',
      header: '狀態',
      cell: (r) => <StatusBadge status={r.status} />,
    },
    {
      id: 'created',
      header: '建立時間',
      cell: (r) => formatDate(r.created_at),
    },
    {
      id: 'updated',
      header: '更新時間',
      cell: (r) => formatDate(r.updated_at),
    },
    {
      id: 'actions',
      header: '',
      className: 'w-[1%] whitespace-nowrap',
      cell: (r) => (
        <div className="flex justify-end gap-2">
          <Button asChild variant="outline" size="sm">
            <Link to={routePaths.reviewCase(r.application_id)}>查看案件</Link>
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
      emptyMessage="沒有符合的任務"
    />
  )
}
