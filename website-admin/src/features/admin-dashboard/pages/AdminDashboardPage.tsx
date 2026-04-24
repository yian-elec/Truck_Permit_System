import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { SectionCard } from '@/shared/ui'

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
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { to: routePaths.reviewTasks, label: '待審任務', desc: '審核申請案件' },
          { to: routePaths.ruleList, label: '規則管理', desc: '設定通行限制規則' },
          { to: routePaths.mapImports, label: '圖資管理', desc: '匯入路網圖層' },
          { to: routePaths.ops, label: '系統查詢', desc: '稽核與作業紀錄' },
        ].map(({ to, label, desc }) => (
          <Link
            key={to}
            to={to}
            className="rounded-xl border border-border bg-card p-4 shadow-sm transition-shadow hover:shadow-md"
          >
            <p className="text-sm font-semibold text-foreground">{label}</p>
            <p className="mt-0.5 text-xs text-muted-foreground">{desc}</p>
          </Link>
        ))}
      </div>

      <AdminMetricsCards
        loading={countsQuery.isLoading}
        totalOpen={countsQuery.data?.total_open_tasks}
        inReview={countsQuery.data?.in_review_tasks}
        payloadMetrics={metricsPayload}
      />

      <SectionCard title="最近活動">
        <AdminOpsFeed loading={modelQuery.isLoading} feed={opsFeedPayload} />
      </SectionCard>

    </div>
  )
}
