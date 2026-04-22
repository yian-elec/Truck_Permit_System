import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import {
  APPLICATION_LIST_STATUS_FILTER_OPTIONS,
  formatApplicationStatus,
} from '@/shared/utils/format-application-status'
import { formatDate } from '@/shared/utils/format-date'
import { Button, EmptyState, Input, PageContainer, SectionCard, Select } from '@/shared/ui'

import { useMyApplications } from '@/features/applicant-home/hooks/useMyApplications'

import type { ApplicationSummary } from '@/features/applicant-home/api/get-my-applications'
import { isApplicantApplicationEditableStatus } from '@/features/application/lib/application-edit-access'

const PAGE_SIZE = 10

function sortByUpdatedDesc(apps: ApplicationSummary[]) {
  return [...apps].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
  )
}

export function ApplicationListPage() {
  const { data, isLoading, error } = useMyApplications()
  const [statusFilter, setStatusFilter] = useState('')
  const [keyword, setKeyword] = useState('')
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)

  const filtered = useMemo(() => {
    const list = data?.applications ?? []
    return sortByUpdatedDesc(
      list.filter((a) => {
        if (statusFilter && a.status !== statusFilter) return false
        if (keyword && !a.application_no.toLowerCase().includes(keyword.toLowerCase())) return false
        return true
      }),
    )
  }, [data?.applications, statusFilter, keyword])

  useEffect(() => {
    setVisibleCount(PAGE_SIZE)
  }, [statusFilter, keyword])

  const visibleRows = useMemo(
    () => filtered.slice(0, visibleCount),
    [filtered, visibleCount],
  )
  const canLoadMore = filtered.length > visibleCount

  if (isLoading) {
    return <PageContainer>載入中…</PageContainer>
  }

  if (error) {
    return <PageContainer className="text-destructive">無法載入案件列表。</PageContainer>
  }

  return (
    <PageContainer as="main" className="space-y-6 py-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">我的案件</h1>
          <p className="text-sm text-muted-foreground">依狀態或案號篩選；列表依最近更新排序。</p>
        </div>
        <Button asChild>
          <Link to={routePaths.applicantApplicationNew}>建立新案件</Link>
        </Button>
      </div>
      <div className="flex flex-wrap items-end gap-3">
        <div className="w-full max-w-xs space-y-1.5">
          <label htmlFor="list-status-filter" className="text-sm font-medium text-foreground">
            狀態
          </label>
          <Select
            id="list-status-filter"
            aria-label="依狀態篩選"
            className="max-w-xs"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={APPLICATION_LIST_STATUS_FILTER_OPTIONS}
          />
        </div>
        <div className="w-full max-w-xs space-y-1.5">
          <label htmlFor="list-keyword-filter" className="text-sm font-medium text-foreground">
            案號
          </label>
          <Input
            id="list-keyword-filter"
            placeholder="搜尋案號"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>
      </div>
      {filtered.length === 0 ? (
        <EmptyState title="沒有符合的案件" description="請建立新案件。" />
      ) : (
        <SectionCard className="space-y-4">
          <ul className="divide-y divide-border">
            {visibleRows.map((app: ApplicationSummary) => (
              <li key={app.application_id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <div>
                  <p className="font-medium">{app.application_no}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatApplicationStatus(app.status)} · {app.applicant_type} ·{' '}
                    {formatDate(app.updated_at)}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm" asChild>
                    <Link to={routePaths.applicantApplication(app.application_id)}>查看</Link>
                  </Button>
                  {isApplicantApplicationEditableStatus(app.status) ? (
                    <Button variant="outline" size="sm" asChild>
                      <Link to={routePaths.applicantApplicationEdit(app.application_id)}>編輯</Link>
                    </Button>
                  ) : null}
                  <Button variant="outline" size="sm" asChild>
                    <Link to={routePaths.applicantApplicationSupplement(app.application_id)}>
                      補件
                    </Link>
                  </Button>
                </div>
              </li>
            ))}
          </ul>
          {canLoadMore ? (
            <div className="flex justify-center border-t border-border pt-4">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
              >
                載入更多
              </Button>
            </div>
          ) : null}
        </SectionCard>
      )}
    </PageContainer>
  )
}
