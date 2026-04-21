import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { PageContainer, Spinner } from '@/shared/ui'

import { useAuthStore } from '@/features/auth/store/auth.store'

import { ConsentSummaryCard } from '../components/ConsentSummaryCard'
import { HandlingUnitsPanel } from '../components/HandlingUnitsPanel'
import { RequiredDocumentsPanel } from '../components/RequiredDocumentsPanel'
import { ServiceOverview } from '../components/ServiceOverview'
import { useConsentLatest } from '../hooks/useConsentLatest'
import { useHandlingUnits } from '../hooks/useHandlingUnits'
import { useRequiredDocuments } from '../hooks/useRequiredDocuments'
import { useServiceOverview } from '../hooks/useServiceOverview'

export function ServiceHomePage() {
  const accessToken = useAuthStore((s) => s.accessToken)
  const overview = useServiceOverview()
  const consent = useConsentLatest()
  const docs = useRequiredDocuments()
  const units = useHandlingUnits()

  const loading =
    overview.isLoading || consent.isLoading || docs.isLoading || units.isLoading
  const error =
    overview.error ?? consent.error ?? docs.error ?? units.error

  if (loading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  if (error || !overview.data || !consent.data || !docs.data || !units.data) {
    return (
      <PageContainer>
        <p className="text-destructive">無法載入公開服務資訊。</p>
      </PageContainer>
    )
  }

  const startHref = accessToken ? routePaths.applicant : routePaths.login

  return (
    <PageContainer as="main" className="space-y-8 py-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">重型貨車通行證</h1>
          <p className="mt-2 text-muted-foreground">
            線上申請與管理通行證。開始前請確認應備文件與同意條款。
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:opacity-90"
            to={startHref}
          >
            開始申請
          </Link>
          <Link
            className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-4 text-sm hover:bg-muted"
            to={routePaths.login}
          >
            登入
          </Link>
          <Link
            className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-4 text-sm hover:bg-muted"
            to={routePaths.register}
          >
            註冊
          </Link>
        </div>
      </div>

      <ServiceOverview data={overview.data} />

      <div className="grid gap-6 lg:grid-cols-2">
        <RequiredDocumentsPanel data={docs.data} />
        <HandlingUnitsPanel data={units.data} />
      </div>

      <ConsentSummaryCard data={consent.data} />
    </PageContainer>
  )
}
