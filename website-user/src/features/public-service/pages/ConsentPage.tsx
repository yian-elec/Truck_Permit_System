import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { PageContainer, Spinner } from '@/shared/ui'

import { useConsentLatest } from '../hooks/useConsentLatest'

export function ConsentPage() {
  const { data, isLoading, error } = useConsentLatest()

  if (isLoading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  if (error || !data) {
    return (
      <PageContainer>
        <p className="text-destructive">無法載入同意條款。</p>
        <Link className="mt-4 inline-block text-primary underline" to={routePaths.home}>
          返回首頁
        </Link>
      </PageContainer>
    )
  }

  return (
    <PageContainer as="main" className="max-w-3xl space-y-6 py-10">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">服務條款</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          版本 {data.version} · 生效日 {data.effective_at}
        </p>
      </div>
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <p className="whitespace-pre-wrap text-muted-foreground">{data.summary}</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <Link
          className="inline-flex h-9 items-center justify-center rounded-md border border-border px-4 text-sm hover:bg-muted"
          to={routePaths.home}
        >
          返回首頁
        </Link>
        <Link
          className="inline-flex h-9 items-center justify-center rounded-md border border-border px-4 text-sm hover:bg-muted"
          to={routePaths.login}
        >
          前往登入
        </Link>
        <Link
          className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:opacity-90"
          to={routePaths.applicant}
        >
          前往申請專區
        </Link>
      </div>
    </PageContainer>
  )
}
