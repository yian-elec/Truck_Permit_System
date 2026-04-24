import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Download, Shield, Clock, CheckCircle, Truck, FileText, HelpCircle } from 'lucide-react'

import { withReturnQuery } from '@/features/auth/lib/safe-return-url'
import { routePaths } from '@/shared/constants/route-paths'
import { PageContainer } from '@/shared/ui'

import { useAuthStore } from '@/features/auth/store/auth.store'

import { CaseDescriptionContent } from '../components/CaseDescriptionContent'
import { FormDownloadDialog } from '../components/FormDownloadDialog'

const highlights = [
  {
    icon: FileText,
    title: '線上申請',
    desc: '全程線上填寫，免排隊，隨時查詢案件進度。',
    color: 'text-blue-600 bg-blue-50 border-blue-100 dark:bg-blue-900/20 dark:border-blue-900/30 dark:text-blue-400',
  },
  {
    icon: Clock,
    title: '即時追蹤',
    desc: '申請送出後，可即時查詢審核狀態與歷程。',
    color: 'text-amber-600 bg-amber-50 border-amber-100 dark:bg-amber-900/20 dark:border-amber-900/30 dark:text-amber-400',
  },
  {
    icon: Shield,
    title: '安全可靠',
    desc: '採用加密傳輸，保護您的個人資料安全。',
    color: 'text-emerald-600 bg-emerald-50 border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-900/30 dark:text-emerald-400',
  },
  {
    icon: CheckCircle,
    title: '快速核發',
    desc: '審核通過後即可下載通行證，加速作業流程。',
    color: 'text-purple-600 bg-purple-50 border-purple-100 dark:bg-purple-900/20 dark:border-purple-900/30 dark:text-purple-400',
  },
]

export function ServiceHomePage() {
  const accessToken = useAuthStore((s) => s.accessToken)
  const [formOpen, setFormOpen] = useState(false)

  const startHref = accessToken
    ? routePaths.applicantApplicationNew
    : withReturnQuery(routePaths.login, routePaths.applicantApplicationNew)

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Banner */}
      <div className="relative overflow-hidden border-b border-border bg-sidebar">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-sidebar-active blur-3xl" />
          <div className="absolute -bottom-10 left-20 h-60 w-60 rounded-full bg-blue-400 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 rounded-full border border-sidebar-muted bg-sidebar-muted/50 px-3 py-1">
                <Truck className="h-3.5 w-3.5 text-sidebar-muted-foreground" />
                <span className="text-xs font-medium text-sidebar-muted-foreground">
                  新北市政府警察局交通警察大隊
                </span>
              </div>
              <h1 className="text-3xl font-bold tracking-tight text-sidebar-foreground sm:text-4xl">
                重型貨車通行證
              </h1>
              <p className="max-w-xl text-sidebar-muted-foreground">
                線上申請與管理大貨車臨時通行證，快速、便利、全程數位化。
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                to={startHref}
                className="inline-flex items-center gap-2 rounded-lg bg-sidebar-active px-5 py-2.5 text-sm font-semibold text-sidebar-active-foreground shadow-sm transition-opacity hover:opacity-90"
              >
                立即申請
                <ArrowRight className="h-4 w-4" />
              </Link>
              <button
                type="button"
                onClick={() => setFormOpen(true)}
                className="inline-flex items-center gap-2 rounded-lg border border-sidebar-muted bg-sidebar-muted/50 px-5 py-2.5 text-sm font-semibold text-sidebar-foreground transition-colors hover:bg-sidebar-muted"
              >
                <Download className="h-4 w-4" />
                書表下載
              </button>
            </div>
          </div>
        </div>
      </div>

      <PageContainer as="main" className="space-y-8 py-8">
        {/* Highlights */}
        <div>
          <h2 className="mb-4 text-lg font-semibold text-foreground">服務特色</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {highlights.map(({ icon: Icon, title, desc, color }) => (
              <div
                key={title}
                className="rounded-xl border border-border bg-background p-5 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className={`mb-3 inline-flex rounded-lg border p-2.5 ${color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mb-1 font-semibold text-foreground">{title}</h3>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Case Description */}
        <div>
          <h2 className="mb-4 text-lg font-semibold text-foreground">申請詳細資訊</h2>
          <CaseDescriptionContent />
        </div>

        {/* CTA */}
        <div className="rounded-xl border border-primary/20 bg-primary/5 p-6 text-center">
          <HelpCircle className="mx-auto mb-3 h-8 w-8 text-primary/60" />
          <h3 className="mb-1 font-semibold text-foreground">準備好開始申請了嗎？</h3>
          <p className="mb-4 text-sm text-muted-foreground">填寫申請資料，我們將在審核後盡速通知您。</p>
          <Link
            to={startHref}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
          >
            開始申請
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </PageContainer>

      <FormDownloadDialog open={formOpen} onOpenChange={setFormOpen} />
    </div>
  )
}
