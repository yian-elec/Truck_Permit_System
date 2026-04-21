import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { formatApplicationStatus } from '@/shared/utils/format-application-status'
import { formatDate } from '@/shared/utils/format-date'
import { Button, EmptyState, Input, PageContainer, SectionCard } from '@/shared/ui'

import { useMyApplications } from '@/features/applicant-home/hooks/useMyApplications'

import type { ApplicationSummary } from '@/features/applicant-home/api/get-my-applications'

export function ApplicationListPage() {
  const { data, isLoading, error } = useMyApplications()
  const [statusFilter, setStatusFilter] = useState('')
  const [keyword, setKeyword] = useState('')

  const filtered = useMemo(() => {
    const list = data?.applications ?? []
    return list.filter((a) => {
      if (statusFilter && a.status !== statusFilter) return false
      if (keyword && !a.application_no.toLowerCase().includes(keyword.toLowerCase())) return false
      return true
    })
  }, [data?.applications, statusFilter, keyword])

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
          <p className="text-sm text-muted-foreground">篩選並開啟案件。</p>
        </div>
        <Button asChild>
          <Link to={routePaths.applicantApplicationNew}>新增案件</Link>
        </Button>
      </div>
      <div className="flex flex-wrap gap-3">
        <Input
          placeholder="依狀態篩選（須完全一致）"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="max-w-xs"
        />
        <Input
          placeholder="搜尋案號"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          className="max-w-xs"
        />
      </div>
      {filtered.length === 0 ? (
        <EmptyState title="沒有符合的案件" description="請建立新案件。" />
      ) : (
        <SectionCard>
          <ul className="divide-y divide-border">
            {filtered.map((app: ApplicationSummary) => (
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
                  <Button variant="outline" size="sm" asChild>
                    <Link to={routePaths.applicantApplicationEdit(app.application_id)}>編輯</Link>
                  </Button>
                  <Button variant="outline" size="sm" asChild>
                    <Link to={routePaths.applicantApplicationSupplement(app.application_id)}>
                      補件
                    </Link>
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </SectionCard>
      )}
    </PageContainer>
  )
}
