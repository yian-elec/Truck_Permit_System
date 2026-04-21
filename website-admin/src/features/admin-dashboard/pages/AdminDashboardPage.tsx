import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { Button, JsonPreview, SectionCard } from '@/shared/ui'

import { getAdminDashboardModel, getReviewDashboardCounts } from '../api/dashboard-api'
import { AdminMetricsCards } from '../components/AdminMetricsCards'
import { AdminOpsFeed } from '../components/AdminOpsFeed'

export function AdminDashboardPage() {
  const modelQuery = useQuery({
    queryKey: queryKeys.admin.dashboardModel,
    queryFn: getAdminDashboardModel,
  })
  const countsQuery = useQuery({
    queryKey: queryKeys.review.dashboard,
    queryFn: getReviewDashboardCounts,
  })

  const payload = modelQuery.data?.payload_by_section ?? {}
  const metricsPayload = payload['admin.dashboard.metrics'] as Record<string, unknown> | undefined
  const opsFeedPayload = payload['admin.dashboard.ops_feed'] as Record<string, unknown> | undefined

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        <Button asChild variant="outline" size="sm">
          <Link to={routePaths.reviewTasks}>前往待審任務</Link>
        </Button>
        <Button asChild variant="outline" size="sm">
          <Link to={routePaths.ruleList}>前往規則管理</Link>
        </Button>
        <Button asChild variant="outline" size="sm">
          <Link to={routePaths.mapImports}>前往圖資管理</Link>
        </Button>
        <Button asChild variant="outline" size="sm">
          <Link to={routePaths.ops}>前往 Ops</Link>
        </Button>
      </div>

      <AdminMetricsCards
        loading={countsQuery.isLoading}
        totalOpen={countsQuery.data?.total_open_tasks}
        inReview={countsQuery.data?.in_review_tasks}
        payloadMetrics={metricsPayload}
      />

      <SectionCard title="Ops 活動流" description="來自 Page Model 之 ops_activity_feed（若後端尚未填入則為空）">
        <AdminOpsFeed loading={modelQuery.isLoading} feed={opsFeedPayload} />
      </SectionCard>

      {import.meta.env.DEV && modelQuery.data ? (
        <SectionCard title="Page model（開發除錯）" description="正式環境不顯示">
          <JsonPreview value={modelQuery.data} />
        </SectionCard>
      ) : null}
    </div>
  )
}
