import { Link, useParams } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { PageContainer, SectionCard, Spinner } from '@/shared/ui'

import { PermitDocumentsPanel } from '../components/PermitDocumentsPanel'
import { PermitSummaryCard } from '../components/PermitSummaryCard'
import { useApplicationPermit } from '../hooks/useApplicationPermit'

export function PermitPage() {
  const { applicationId = '' } = useParams()
  const permit = useApplicationPermit(applicationId)

  if (permit.isLoading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  if (permit.isError) {
    return (
      <PageContainer as="main" className="space-y-6 py-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h1 className="text-2xl font-semibold">通行證</h1>
          <Link
            className="text-sm text-primary underline"
            to={routePaths.applicantApplication(applicationId)}
          >
            返回案件詳情
          </Link>
        </div>
        <SectionCard title="通行證">
          <p className="text-sm text-muted-foreground">無法載入通行證資料。</p>
        </SectionCard>
      </PageContainer>
    )
  }

  if (!permit.data) {
    return (
      <PageContainer as="main" className="space-y-6 py-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h1 className="text-2xl font-semibold">通行證</h1>
          <Link
            className="text-sm text-primary underline"
            to={routePaths.applicantApplication(applicationId)}
          >
            返回案件詳情
          </Link>
        </div>
        <SectionCard title="通行證">
          <p className="text-sm text-muted-foreground">本案尚未核發通行證。</p>
        </SectionCard>
      </PageContainer>
    )
  }

  return (
    <PageContainer as="main" className="space-y-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">通行證</h1>
        <Link
          className="text-sm text-primary underline"
          to={routePaths.applicantApplication(applicationId)}
        >
          返回案件詳情
        </Link>
      </div>
      <PermitSummaryCard data={permit.data} />
      <PermitDocumentsPanel applicationId={applicationId} />
    </PageContainer>
  )
}
