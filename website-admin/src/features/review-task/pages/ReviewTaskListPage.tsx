import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import { queryKeys } from '@/shared/constants/query-keys'
import { FilterBar, SectionCard } from '@/shared/ui'

import { listReviewTasks } from '../api/review-task-api'
import { AssignTaskDialog } from '../components/AssignTaskDialog'
import { ReviewTaskFilters } from '../components/ReviewTaskFilters'
import { ReviewTaskTable } from '../components/ReviewTaskTable'

const PAGE_SIZE = 50

export function ReviewTaskListPage() {
  const [keyword, setKeyword] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [stageFilter, setStageFilter] = useState('')
  const [assignAppId, setAssignAppId] = useState<string | null>(null)

  const tasksQuery = useQuery({
    queryKey: [...queryKeys.review.tasks, PAGE_SIZE, 0] as const,
    queryFn: () => listReviewTasks({ limit: PAGE_SIZE, offset: 0 }),
  })

  const filtered = useMemo(() => {
    const rows = tasksQuery.data ?? []
    return rows.filter((t) => {
      if (statusFilter && !t.status.toLowerCase().includes(statusFilter.toLowerCase())) return false
      if (stageFilter && !t.stage.toLowerCase().includes(stageFilter.toLowerCase())) return false
      if (keyword) {
        const k = keyword.toLowerCase()
        if (
          !t.application_id.toLowerCase().includes(k) &&
          !t.review_task_id.toLowerCase().includes(k)
        ) {
          return false
        }
      }
      return true
    })
  }, [tasksQuery.data, keyword, statusFilter, stageFilter])

  return (
    <div className="space-y-4">
      <SectionCard title="審查任務" description="承辦工作台任務列表">
        <FilterBar>
          <ReviewTaskFilters
            keyword={keyword}
            onKeywordChange={setKeyword}
            status={statusFilter}
            onStatusChange={setStatusFilter}
            stage={stageFilter}
            onStageChange={setStageFilter}
          />
        </FilterBar>
        <div className="mt-4">
          {tasksQuery.isLoading ? (
            <p className="text-muted-foreground text-sm">載入中…</p>
          ) : tasksQuery.isError ? (
            <p className="text-destructive text-sm">無法載入任務列表</p>
          ) : (
            <ReviewTaskTable tasks={filtered} onAssign={(id) => setAssignAppId(id)} />
          )}
        </div>
      </SectionCard>

      <AssignTaskDialog
        open={assignAppId != null}
        onOpenChange={(o) => !o && setAssignAppId(null)}
        applicationId={assignAppId}
      />
    </div>
  )
}
