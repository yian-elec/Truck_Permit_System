import { Link, useParams } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { usePageTitle } from '@/shared/hooks'
import { PageContainer, SectionCard, Spinner, Button } from '@/shared/ui'
import { formatApplicationStatus } from '@/shared/utils/format-application-status'
import { formatDate } from '@/shared/utils/format-date'

import { ApplicationFlowStepper } from '../components/ApplicationFlowStepper'
import { useApplicationDetail } from '../hooks/useApplicationDetail'

export function ApplicationSubmitCompletePage() {
  const { applicationId = '' } = useParams()
  usePageTitle(`送件完成 ${applicationId}`)

  const detail = useApplicationDetail(applicationId)

  if (detail.isLoading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  if (!detail.data) {
    return <PageContainer>找不到案件</PageContainer>
  }

  const d = detail.data

  return (
    <PageContainer as="main" className="space-y-6 py-8">
      <ApplicationFlowStepper phase="complete" />

      <SectionCard title="送件成功">
        <p className="text-sm text-muted-foreground">
          您的申請已送出，承辦單位將依程序審查。您可隨時於「我的案件」查看進度。
        </p>
        <dl className="mt-4 grid gap-3 text-sm">
          <div>
            <dt className="text-muted-foreground">案件編號</dt>
            <dd className="text-lg font-semibold">{d.application_no}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">送件時間</dt>
            <dd>{d.submitted_at ? formatDate(d.submitted_at) : '—'}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">目前狀態</dt>
            <dd>{formatApplicationStatus(d.status)}</dd>
          </div>
        </dl>
        <div className="mt-6 flex flex-wrap gap-2">
          <Button asChild>
            <Link to={routePaths.applicantApplication(applicationId)}>查看案件</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to={routePaths.applicant}>返回我的案件</Link>
          </Button>
        </div>
      </SectionCard>
    </PageContainer>
  )
}
