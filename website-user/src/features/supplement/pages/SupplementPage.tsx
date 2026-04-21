import { Link, useParams } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { PageContainer, SectionCard, Spinner } from '@/shared/ui'

import { SupplementRequestList } from '../components/SupplementRequestList'
import { SupplementResponseForm } from '../components/SupplementResponseForm'
import { useSupplementRequests } from '../hooks/useSupplementRequests'

export function SupplementPage() {
  const { applicationId = '' } = useParams()
  const requests = useSupplementRequests(applicationId)

  if (requests.isLoading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  return (
    <PageContainer as="main" className="space-y-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">補件</h1>
        <Link
          className="text-sm text-primary underline"
          to={routePaths.applicantApplication(applicationId)}
        >
          返回案件詳情
        </Link>
      </div>
      <SectionCard title="補件通知">
        <SupplementRequestList data={requests.data} />
      </SectionCard>
      <SupplementResponseForm applicationId={applicationId} requests={requests.data} />
    </PageContainer>
  )
}
