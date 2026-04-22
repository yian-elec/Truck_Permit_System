import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { PlusCircle, FileText, Clock, CheckCircle2, AlertCircle, Search, Filter } from 'lucide-react'

import { routePaths } from '@/shared/constants/route-paths'
import {
  APPLICATION_LIST_STATUS_FILTER_OPTIONS,
  formatApplicationStatus,
} from '@/shared/utils/format-application-status'
import { formatDate } from '@/shared/utils/format-date'
import { Button, EmptyState, Input, PageContainer, SectionCard, Select, StatusBadge } from '@/shared/ui'

import { useMyApplications } from '@/features/applicant-home/hooks/useMyApplications'

import type { ApplicationSummary } from '@/features/applicant-home/api/get-my-applications'
import { isApplicantApplicationEditableStatus } from '@/features/application/lib/application-edit-access'

const PAGE_SIZE = 10

function sortByUpdatedDesc(apps: ApplicationSummary[]) {
  return [...apps].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
  )
}

function getStatusVariant(status: string): 'default' | 'success' | 'warning' | 'destructive' {
  if (['approved'].includes(status)) return 'success'
  if (['under_review', 'submitted', 'resubmitted'].includes(status)) return 'warning'
  if (['rejected', 'cancelled', 'withdrawn'].includes(status)) return 'destructive'
  return 'default'
}

function getStatusIcon(status: string) {
  if (status === 'approved') return <CheckCircle2 className="h-4 w-4 text-emerald-600" />
  if (['under_review', 'submitted', 'resubmitted'].includes(status)) return <Clock className="h-4 w-4 text-amber-600" />
  if (['rejected', 'cancelled', 'withdrawn'].includes(status)) return <AlertCircle className="h-4 w-4 text-destructive" />
  return <FileText className="h-4 w-4 text-muted-foreground" />
}

export function ApplicationListPage() {
  const { data, isLoading, error } = useMyApplications()
  const [statusFilter, setStatusFilter] = useState('')
  const [keyword, setKeyword] = useState('')
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)

  const allApps = data?.applications ?? []

  // Stats
  const stats = useMemo(() => ({
    total: allApps.length,
    pending: allApps.filter(a => ['submitted', 'resubmitted', 'under_review'].includes(a.status)).length,
    approved: allApps.filter(a => a.status === 'approved').length,
    supplement: allApps.filter(a => a.status === 'supplement_required').length,
  }), [allApps])

  const filtered = useMemo(() => {
    const list = allApps
    return sortByUpdatedDesc(
      list.filter((a) => {
        if (statusFilter && a.status !== statusFilter) return false
        if (keyword && !a.application_no.toLowerCase().includes(keyword.toLowerCase())) return false
        return true
      }),
    )
  }, [allApps, statusFilter, keyword])

  useEffect(() => {
    setVisibleCount(PAGE_SIZE)
  }, [statusFilter, keyword])

  const visibleRows = useMemo(() => filtered.slice(0, visibleCount), [filtered, visibleCount])
  const canLoadMore = filtered.length > visibleCount

  if (isLoading) {
    return (
      <PageContainer className="py-8">
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-sm">載入中…</span>
        </div>
      </PageContainer>
    )
  }

  if (error) {
    return (
      <PageContainer className="py-8">
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
          無法載入案件列表，請重新整理頁面。
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer as="main" className="space-y-6 py-8">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">我的案件</h1>
          <p className="mt-1 text-sm text-muted-foreground">管理您提交的所有通行證申請。</p>
        </div>
        <Button asChild size="sm" className="gap-2">
          <Link to={routePaths.applicantApplicationNew}>
            <PlusCircle className="h-4 w-4" />
            建立新案件
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      {allApps.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-xl border border-border bg-background p-4 shadow-sm">
            <p className="text-xs font-medium text-muted-foreground">全部案件</p>
            <p className="mt-1.5 text-2xl font-bold text-foreground">{stats.total}</p>
          </div>
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm dark:border-amber-900/30 dark:bg-amber-900/10">
            <p className="text-xs font-medium text-amber-700 dark:text-amber-400">審核中</p>
            <p className="mt-1.5 text-2xl font-bold text-amber-800 dark:text-amber-300">{stats.pending}</p>
          </div>
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm dark:border-emerald-900/30 dark:bg-emerald-900/10">
            <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400">已核准</p>
            <p className="mt-1.5 text-2xl font-bold text-emerald-800 dark:text-emerald-300">{stats.approved}</p>
          </div>
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 shadow-sm dark:border-blue-900/30 dark:bg-blue-900/10">
            <p className="text-xs font-medium text-blue-700 dark:text-blue-400">待補件</p>
            <p className="mt-1.5 text-2xl font-bold text-blue-800 dark:text-blue-300">{stats.supplement}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex min-w-[160px] flex-1 items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 shadow-sm">
          <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
          <input
            id="list-keyword-filter"
            placeholder="搜尋案號…"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select
            id="list-status-filter"
            aria-label="依狀態篩選"
            className="max-w-[160px]"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={APPLICATION_LIST_STATUS_FILTER_OPTIONS}
          />
        </div>
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <EmptyState
          title="沒有符合的案件"
          description={allApps.length === 0 ? '您尚未建立任何案件，點擊上方按鈕開始申請。' : '請調整篩選條件。'}
        />
      ) : (
        <div className="space-y-3">
          {visibleRows.map((app: ApplicationSummary) => (
            <div
              key={app.application_id}
              className="group rounded-xl border border-border bg-background p-4 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                {/* Left */}
                <div className="flex min-w-0 items-start gap-3">
                  <div className="mt-0.5 rounded-lg border border-border bg-muted p-2">
                    {getStatusIcon(app.status)}
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-semibold text-foreground">{app.application_no}</p>
                    <div className="mt-1 flex flex-wrap items-center gap-2">
                      <StatusBadge variant={getStatusVariant(app.status)}>
                        {formatApplicationStatus(app.status)}
                      </StatusBadge>
                      <span className="text-xs text-muted-foreground">{app.applicant_type}</span>
                      <span className="text-xs text-muted-foreground">·</span>
                      <span className="text-xs text-muted-foreground">更新 {formatDate(app.updated_at)}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex shrink-0 flex-wrap gap-2">
                  <Button variant="outline" size="sm" asChild>
                    <Link to={routePaths.applicantApplication(app.application_id)}>查看</Link>
                  </Button>
                  {isApplicantApplicationEditableStatus(app.status) && (
                    <Button variant="outline" size="sm" asChild>
                      <Link to={routePaths.applicantApplicationEdit(app.application_id)}>編輯</Link>
                    </Button>
                  )}
                  <Button variant="outline" size="sm" asChild>
                    <Link to={routePaths.applicantApplicationSupplement(app.application_id)}>補件</Link>
                  </Button>
                </div>
              </div>
            </div>
          ))}

          {canLoadMore && (
            <div className="flex justify-center pt-2">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
              >
                載入更多（還有 {filtered.length - visibleCount} 筆）
              </Button>
            </div>
          )}
        </div>
      )}
    </PageContainer>
  )
}
