import { PageContainer, SectionCard, Spinner } from '@/shared/ui'

import { useApplicantHomePageModel } from '@/features/page-model/hooks/useApplicantHomePageModel'

import { ApplicantHomeHeader } from '../components/ApplicantHomeHeader'
import { MyApplicationsPreview } from '../components/MyApplicationsPreview'
import { QuickActions } from '../components/QuickActions'
import { useMyApplications } from '../hooks/useMyApplications'

export function ApplicantHomePage() {
  const pageModel = useApplicantHomePageModel()
  const apps = useMyApplications()

  if (pageModel.isLoading || apps.isLoading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  return (
    <PageContainer as="main" className="space-y-8 py-8">
      <ApplicantHomeHeader />
      <SectionCard title="快速操作">
        <QuickActions />
      </SectionCard>
      <SectionCard title="我的案件" description="最近案件">
        {apps.data?.applications ? (
          <MyApplicationsPreview applications={apps.data.applications} />
        ) : null}
      </SectionCard>
      {pageModel.data?.sections?.length ? (
        <SectionCard title="頁面區塊" description="由 application-home-model 驅動">
          <ul className="list-inside list-disc text-sm text-muted-foreground">
            {pageModel.data.sections
              .slice()
              .sort((a, b) => a.sort_order - b.sort_order)
              .map((s) => (
                <li key={s.section_code}>{s.section_code}</li>
              ))}
          </ul>
        </SectionCard>
      ) : null}
    </PageContainer>
  )
}
