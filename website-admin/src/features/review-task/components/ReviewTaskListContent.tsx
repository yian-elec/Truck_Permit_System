import { useQueries, useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import { queryKeys } from '@/shared/constants/query-keys'
import { summarizeApplicationForTaskList } from '@/shared/utils/admin-operator-copy'
import { FilterBar, SectionCard } from '@/shared/ui'

import { getReviewApplication } from '@/features/review-case/api/review-case-api'
import { listReviewTasks, type ReviewTaskSummary } from '../api/review-task-api'
import { AssignTaskDialog } from './AssignTaskDialog'
import { ReviewTaskFilters } from './ReviewTaskFilters'
import { ReviewTaskTable } from './ReviewTaskTable'

const PAGE_SIZE = 50

export type EnrichedReviewTask = ReviewTaskSummary & {
  application_no: string
  applicant_name: string
  plate: string
  period_label: string
  case_loading: boolean
  case_error: boolean
}

type Props = {
  /**
   * 內嵌於作業中心時不包外層「審查任務」SectionCard，避免重複標題。
   */
  embedded?: boolean
}

export function ReviewTaskListContent({ embedded = false }: Props) {
  const [keyword, setKeyword] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [stageFilter, setStageFilter] = useState('')
  const [assignAppId, setAssignAppId] = useState<string | null>(null)

  const tasksQuery = useQuery({
    queryKey: [...queryKeys.review.tasks, PAGE_SIZE, 0] as const,
    queryFn: () => listReviewTasks({ limit: PAGE_SIZE, offset: 0 }),
  })

  const taskRows = tasksQuery.data ?? []
  const caseQueries = useQueries({
    queries: taskRows.map((t) => ({
      queryKey: queryKeys.review.caseDetail(t.application_id),
      queryFn: () => getReviewApplication(t.application_id),
      enabled: tasksQuery.isSuccess,
      staleTime: 3 * 60_000,
    })),
  })

  const enriched: EnrichedReviewTask[] = useMemo(() => {
    return taskRows.map((t, i) => {
      const q = caseQueries[i]
      const app = (q?.data?.application ?? undefined) as Record<string, unknown> | undefined
      const s = summarizeApplicationForTaskList(app)
      return {
        ...t,
        application_no: s.applicationNo,
        applicant_name: s.applicantName,
        plate: s.plate,
        period_label: s.periodLabel,
        case_loading: q?.isLoading ?? false,
        case_error: q?.isError ?? false,
      }
    })
  }, [taskRows, caseQueries])

  const filtered = useMemo(() => {
    return enriched.filter((t) => {
      if (statusFilter && !t.status.toLowerCase().includes(statusFilter.toLowerCase())) return false
      if (stageFilter && !t.stage.toLowerCase().includes(stageFilter.toLowerCase())) return false
      if (keyword) {
        const k = keyword.toLowerCase()
        if (
          !t.application_id.toLowerCase().includes(k) &&
          !t.review_task_id.toLowerCase().includes(k) &&
          !t.application_no.toLowerCase().includes(k) &&
          !t.applicant_name.toLowerCase().includes(k) &&
          !t.plate.toLowerCase().includes(k)
        ) {
          return false
        }
      }
      return true
    })
  }, [enriched, keyword, statusFilter, stageFilter])

  const body = (
    <>
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
    </>
  )

  return (
    <div className="space-y-4">
      {embedded ? body : <SectionCard title="申請審核">{body}</SectionCard>}

      <AssignTaskDialog
        open={assignAppId != null}
        onOpenChange={(o) => !o && setAssignAppId(null)}
        applicationId={assignAppId}
      />
    </div>
  )
}
