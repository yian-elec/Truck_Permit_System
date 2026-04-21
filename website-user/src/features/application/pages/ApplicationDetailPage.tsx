import { Link, useParams } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { PageContainer, SectionCard, Spinner } from '@/shared/ui'

import { PermitSummaryCard } from '@/features/permit/components/PermitSummaryCard'
import { useApplicationPermit } from '@/features/permit/hooks/useApplicationPermit'
import { SupplementRequestList } from '@/features/supplement/components/SupplementRequestList'
import { useSupplementRequests } from '@/features/supplement/hooks/useSupplementRequests'

import { ApplicationSummaryCard } from '../components/ApplicationSummaryCard'
import { ApplicationTimeline } from '../components/ApplicationTimeline'
import { useApplicationDetail } from '../hooks/useApplicationDetail'
import { useTimeline } from '../hooks/useTimeline'

export function ApplicationDetailPage() {
  const { applicationId = '' } = useParams()
  const detail = useApplicationDetail(applicationId)
  const timeline = useTimeline(applicationId)
  const supplements = useSupplementRequests(applicationId)
  const permit = useApplicationPermit(applicationId)

  if (detail.isLoading || timeline.isLoading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  if (!detail.data) {
    return <PageContainer>找不到案件。</PageContainer>
  }

  return (
    <PageContainer as="main" className="space-y-6 py-8">
      <ApplicationSummaryCard detail={detail.data} />
      <div className="flex flex-wrap gap-2">
        <Link
          className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm text-primary-foreground"
          to={routePaths.applicantApplicationEdit(applicationId)}
        >
          編輯
        </Link>
        <Link
          className="inline-flex h-9 items-center justify-center rounded-md border border-border px-4 text-sm"
          to={routePaths.applicantApplicationSupplement(applicationId)}
        >
          補件
        </Link>
        <Link
          className="inline-flex h-9 items-center justify-center rounded-md border border-border px-4 text-sm"
          to={routePaths.applicantApplicationPermit(applicationId)}
        >
          通行證
        </Link>
      </div>
      <SectionCard title="案件歷程">
        {timeline.data ? <ApplicationTimeline timeline={timeline.data} /> : null}
      </SectionCard>
      <SectionCard title="補件通知">
        {supplements.isLoading ? (
          <Spinner />
        ) : (
          <SupplementRequestList data={supplements.data} />
        )}
      </SectionCard>
      {permit.isLoading ? (
        <SectionCard title="通行證摘要">
          <Spinner />
        </SectionCard>
      ) : permit.isError ? (
        <SectionCard title="通行證摘要">
          <p className="text-sm text-muted-foreground">尚無通行證或無法載入。</p>
        </SectionCard>
      ) : permit.data ? (
        <PermitSummaryCard data={permit.data} />
      ) : (
        <SectionCard title="通行證摘要">
          <p className="text-sm text-muted-foreground">本案尚未核發通行證。</p>
        </SectionCard>
      )}
    </PageContainer>
  )
}
