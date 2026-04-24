import { useQuery } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths, workCenterUrl } from '@/shared/constants/route-paths'
import { formatDate } from '@/shared/utils/format-date'
import { isNoiseAuditActionCode } from '@/shared/utils/admin-operator-copy'
import { Button, SectionCard } from '@/shared/ui'

import { listMapLayers } from '@/features/admin-map-layer/api/map-layer-api'
import { listAuditLogs, listImportJobs, listNotificationJobs } from '@/features/admin-ops/api/ops-api'

import { getReviewDashboardCounts } from '../api/dashboard-api'

function importJobLooksFailedOrStuck(status: unknown): boolean {
  const s = String(status ?? '').toLowerCase()
  return (
    s.includes('fail') ||
    s.includes('error') ||
    s.includes('dead') ||
    s.includes('stuck') ||
    s.includes('cancel')
  )
}

function notifLooksFailed(status: unknown): boolean {
  const s = String(status ?? '').toLowerCase()
  return s.includes('fail') || s.includes('error')
}

export function AdminDashboardPage() {
  const countsQuery = useQuery({
    queryKey: queryKeys.review.dashboard,
    queryFn: getReviewDashboardCounts,
  })
  const importJobsQuery = useQuery({
    queryKey: queryKeys.ops.importJobs,
    queryFn: listImportJobs,
  })
  const notifQuery = useQuery({
    queryKey: queryKeys.ops.notificationJobs,
    queryFn: listNotificationJobs,
  })
  const layersQuery = useQuery({
    queryKey: queryKeys.admin.mapLayers,
    queryFn: listMapLayers,
  })
  const auditQuery = useQuery({
    queryKey: queryKeys.ops.auditLogs,
    queryFn: listAuditLogs,
  })

  const badImports = (importJobsQuery.data ?? []).filter((j) => importJobLooksFailedOrStuck(j.status)).length
  const failedNotif = (notifQuery.data ?? []).filter((j) => notifLooksFailed(j.status)).length

  const publishedLayers = [...(layersQuery.data ?? [])]
    .filter((l) => l.published_at)
    .sort((a, b) => new Date(String(b.published_at)).getTime() - new Date(String(a.published_at)).getTime())

  const recentAudit = [...(auditQuery.data ?? [])]
    .filter((a) => !isNoiseAuditActionCode(String(a.action_code ?? '')))
    .sort((a, b) => {
      const ta = new Date(String(a.created_at ?? 0)).getTime()
      const tb = new Date(String(b.created_at ?? 0)).getTime()
      return tb - ta
    })
    .slice(0, 3)

  const openWait = countsQuery.data?.total_open_tasks ?? 0
  const inReview = countsQuery.data?.in_review_tasks ?? 0

  const attentionLines: string[] = []
  if (badImports > 0) {
    attentionLines.push(`有 ${badImports} 筆圖資匯入狀態異常或需追蹤，請至圖資匯入查看。`)
  }
  if (failedNotif > 0) {
    attentionLines.push(`有 ${failedNotif} 筆通知發送失敗，請至通知紀錄確認。`)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-muted-foreground text-sm">
          今日工作重點：待辦件數、異常提醒與最近動態。
        </p>
        <Button variant="secondary" size="sm" asChild>
          <Link to={workCenterUrl('review')}>前往待處理工作</Link>
        </Button>
      </div>

      <SectionCard title="今日待辦">
        {countsQuery.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <TodoCard
              value={openWait}
              label="件申請等待審核"
              action={<Link className="text-primary text-sm font-medium underline underline-offset-2" to={workCenterUrl('review')}>查看待審申請</Link>}
            />
            <TodoCard
              value={inReview}
              label="件審核中"
              action={<Link className="text-primary text-sm font-medium underline underline-offset-2" to={workCenterUrl('review')}>前往申請審核</Link>}
            />
            <TodoCard
              value={badImports}
              label="件圖資匯入異常"
              action={<Link className="text-primary text-sm font-medium underline underline-offset-2" to={workCenterUrl('import')}>查看匯入狀態</Link>}
            />
            <TodoCard
              value={failedNotif}
              label="件通知發送失敗"
              action={<Link className="text-primary text-sm font-medium underline underline-offset-2" to={workCenterUrl('notif')}>查看通知紀錄</Link>}
            />
          </div>
        )}
      </SectionCard>

      <SectionCard title="需要注意">
        {importJobsQuery.isLoading || notifQuery.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : attentionLines.length === 0 ? (
          <p className="text-foreground text-sm">目前沒有需要處理的異常。</p>
        ) : (
          <ul className="list-inside list-disc space-y-2 text-sm text-foreground">
            {attentionLines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        )}
      </SectionCard>

      <SectionCard title="最近完成與動態">
        {layersQuery.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : (
          <ul className="space-y-3 text-sm">
            <li>
              <span className="text-muted-foreground">最近啟用圖資：</span>
              {publishedLayers[0] ? (
                <span className="text-foreground">
                  {publishedLayers[0].layer_name}（v{publishedLayers[0].version_no}）
                </span>
              ) : (
                <span className="text-muted-foreground">尚無</span>
              )}
            </li>
            <li>
              <span className="text-muted-foreground">最近一週內已結案審查：</span>
              <span className="tabular-nums text-foreground">
                {countsQuery.data?.closed_tasks_in_window ?? '—'} 件
              </span>
            </li>
            <li>
              <span className="text-muted-foreground">最近操作紀錄（節录）：</span>
              {recentAudit.length === 0 ? (
                <span className="text-muted-foreground">尚無可顯示項目</span>
              ) : (
                <ul className="mt-1 space-y-1 border-l-2 border-border pl-3">
                  {recentAudit.map((a) => (
                    <li key={String(a.audit_log_id ?? a.id)} className="text-xs">
                      <span className="text-foreground">{String(a.action_code ?? '—')}</span>
                      <span className="text-muted-foreground"> · {a.created_at ? formatDate(String(a.created_at)) : '—'}</span>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          </ul>
        )}
        <div className="mt-4 flex flex-wrap gap-3">
          <Button variant="outline" size="sm" asChild>
            <Link to={`${routePaths.mapImports}?tab=layers`}>圖資與上傳</Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link to={routePaths.auditLog}>操作紀錄</Link>
          </Button>
        </div>
      </SectionCard>
    </div>
  )
}

function TodoCard({
  value,
  label,
  action,
}: {
  value: number
  label: string
  action: ReactNode
}) {
  return (
    <div className="rounded-xl border border-border bg-background p-4 shadow-sm">
      <p className="text-3xl font-semibold tabular-nums text-foreground">{value}</p>
      <p className="text-muted-foreground mt-1 text-xs">{label}</p>
      <div className="mt-3">{action}</div>
    </div>
  )
}
