import { useState } from 'react'
import { Link } from 'react-router-dom'

import { withReturnQuery } from '@/features/auth/lib/safe-return-url'
import { routePaths } from '@/shared/constants/route-paths'
import { PageContainer, SectionCard, Button } from '@/shared/ui'

import { useAuthStore } from '@/features/auth/store/auth.store'

import { CaseDescriptionContent } from '../components/CaseDescriptionContent'
import { FormDownloadDialog } from '../components/FormDownloadDialog'

export function ServiceHomePage() {
  const accessToken = useAuthStore((s) => s.accessToken)
  const [formOpen, setFormOpen] = useState(false)

  const startHref = accessToken
    ? routePaths.applicantApplicationNew
    : withReturnQuery(routePaths.login, routePaths.applicantApplicationNew)

  return (
    <PageContainer as="main" className="space-y-8 py-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">重型貨車通行證</h1>
          <p className="mt-2 text-muted-foreground">線上申請與管理通行證。以下為案件說明與應備事項。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild>
            <Link to={startHref}>開始申請</Link>
          </Button>
          <Button type="button" variant="outline" onClick={() => setFormOpen(true)}>
            書表下載
          </Button>
        </div>
      </div>

      <FormDownloadDialog open={formOpen} onOpenChange={setFormOpen} />

      <SectionCard title="案件說明" description="新北市政府警察局交通警察大隊辦理之大貨車臨時通行證相關資訊。">
        <CaseDescriptionContent />
      </SectionCard>
    </PageContainer>
  )
}
