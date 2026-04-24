import { useQuery } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { formatOperatorStatus } from '@/shared/utils/admin-operator-copy'
import { SectionCard, Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui'

import { listAuditTrail } from '@/features/review-audit/api/review-audit-api'
import { AuditTrailPanel } from '@/features/review-audit/components/AuditTrailPanel'
import { AttachmentPreviewList } from '@/features/review-attachment/components/AttachmentPreviewList'
import { CommentForm } from '@/features/review-comment/components/CommentForm'
import { CommentList } from '@/features/review-comment/components/CommentList'
import { ApproveDialog } from '@/features/review-decision/components/ApproveDialog'
import { DecisionHistory } from '@/features/review-decision/components/DecisionHistory'
import { RejectDialog } from '@/features/review-decision/components/RejectDialog'
import { SupplementDialog } from '@/features/review-decision/components/SupplementDialog'
import { OcrSummaryPanel } from '@/features/review-ocr/components/OcrSummaryPanel'

import { getReviewApplication } from '../api/review-case-api'
import { ReviewActionBar } from '../components/ReviewActionBar'
import { ReviewCaseHeader } from '../components/ReviewCaseHeader'
import { ReviewCaseSummary } from '../components/ReviewCaseSummary'

export function ReviewCasePage() {
  const { applicationId = '' } = useParams<{ applicationId: string }>()
  const commentSectionRef = useRef<HTMLDivElement>(null)
  const [supOpen, setSupOpen] = useState(false)
  const [apOpen, setApOpen] = useState(false)
  const [rjOpen, setRjOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  const caseQuery = useQuery({
    queryKey: queryKeys.review.caseDetail(applicationId),
    queryFn: () => getReviewApplication(applicationId),
    enabled: Boolean(applicationId),
  })

  const auditQuery = useQuery({
    queryKey: queryKeys.review.auditTrail(applicationId),
    queryFn: () => listAuditTrail(applicationId),
    enabled: Boolean(applicationId),
  })

  const application = (caseQuery.data?.application ?? {}) as Record<string, unknown>
  const attachments = (application.attachments as Record<string, unknown>[] | undefined) ?? []
  const comments = (caseQuery.data?.comments ?? []) as Record<string, unknown>[]
  const decisions = (caseQuery.data?.decisions ?? []) as Record<string, unknown>[]
  const routeSnap = caseQuery.data?.route_plan

  if (caseQuery.isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground py-12 justify-center">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        載入案件中…
      </div>
    )
  }
  if (caseQuery.isError || !caseQuery.data) {
    return <p className="text-destructive text-sm">無法載入案件</p>
  }

  const ocrBlock = (caseQuery.data.ocr_summary ?? null) as Record<string, unknown> | null
  const ocrEmpty = !ocrBlock || Object.keys(ocrBlock).length === 0
  const hasRoute = routeSnap && typeof routeSnap === 'object' && Object.keys(routeSnap).length > 0
  const st = String(application.status ?? '')

  const statusLabel = formatOperatorStatus(st)
  const summaryBits = [
    attachments.length ? '已上傳附件' : '尚未上傳附件',
    ocrEmpty ? '尚無辨識摘要' : '已有辨識摘要',
    hasRoute ? '路線已載入' : '路線待檢查',
  ]

  return (
    <div className="space-y-4 pb-24">
      <SectionCard>
        <ReviewCaseHeader application={application} />
        <p className="text-foreground border-border mt-3 border-t pt-3 text-sm">
          目前狀態：<span className="font-medium">「{statusLabel}」</span>
          <span className="text-muted-foreground"> ・ {summaryBits.join(' ・ ')}</span>
        </p>
      </SectionCard>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="h-auto w-full flex-wrap justify-start gap-1 p-1.5">
          <TabsTrigger value="overview">申請內容</TabsTrigger>
          <TabsTrigger value="attachments">文件附件</TabsTrigger>
          <TabsTrigger value="ocr">文件辨識</TabsTrigger>
          <TabsTrigger value="route">路線檢查</TabsTrigger>
          <TabsTrigger value="comments">
            審核意見
            {comments.length > 0 && (
              <span className="ml-1.5 rounded-full bg-primary/15 px-1.5 py-0.5 text-xs font-medium text-primary">
                {comments.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="history">審查決定</TabsTrigger>
          <TabsTrigger value="audit">系統內部操作</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <SectionCard title="申請內容">
            <ReviewCaseSummary application={application} />
          </SectionCard>
        </TabsContent>

        <TabsContent value="attachments">
          <SectionCard title="文件附件">
            {attachments.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                尚未上傳附件。請待申請人上傳後再檢視；審核意見中也可說明缺件。
              </p>
            ) : null}
            <AttachmentPreviewList applicationId={applicationId} attachments={attachments} />
          </SectionCard>
        </TabsContent>

        <TabsContent value="ocr">
          <SectionCard title="文件辨識（摘錄）">
            <OcrSummaryPanel applicationId={applicationId} />
          </SectionCard>
        </TabsContent>

        <TabsContent value="route">
          <SectionCard title="路線檢查">
            {hasRoute ? (
              <div className="space-y-3">
                <p className="text-sm text-foreground">已載入路線檢查所需資料。若要檢視地圖與風險，請到路線審查畫面。</p>
                <Link
                  className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
                  to={routePaths.reviewRoute(applicationId)}
                >
                  前往路線審查 →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-foreground">此案件尚未執行路線檢查。請點下方前往路線審查，必要時在該畫面完成審理。</p>
                <Link
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border px-4 py-2 text-sm font-medium transition-colors hover:bg-muted"
                  to={routePaths.reviewRoute(applicationId)}
                >
                  前往路線審查
                </Link>
              </div>
            )}
          </SectionCard>
        </TabsContent>

        <TabsContent value="comments">
          <SectionCard title="審核意見">
            <div ref={commentSectionRef}>
              <CommentList comments={comments} />
              <div className="mt-4 border-t border-border pt-4">
                <CommentForm applicationId={applicationId} />
              </div>
            </div>
          </SectionCard>
        </TabsContent>

        <TabsContent value="history">
          <SectionCard title="審查決定">
            <DecisionHistory decisions={decisions} />
          </SectionCard>
        </TabsContent>

        <TabsContent value="audit">
          <SectionCard title="內部操作與日誌">
            {auditQuery.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : auditQuery.data ? (
              <AuditTrailPanel entries={auditQuery.data} />
            ) : (
              <p className="text-destructive text-sm">無法載入</p>
            )}
            <p className="text-muted-foreground mt-3 text-xs">供內部追蹤用，不影響審查員必要操作步驟。</p>
          </SectionCard>
        </TabsContent>
      </Tabs>

      <details className="text-muted-foreground rounded-md border border-border/60 p-3 text-xs">
        <summary className="cursor-pointer font-medium">系統識別碼（內部用）</summary>
        <p className="mt-2 font-mono">申請案：{applicationId}</p>
      </details>

      {/* 固定底部操作列 */}
      <ReviewActionBar
        applicationId={applicationId}
        onSupplement={() => setSupOpen(true)}
        onApprove={() => setApOpen(true)}
        onReject={() => setRjOpen(true)}
        onComment={() => {
          setActiveTab('comments')
          setTimeout(() => commentSectionRef.current?.scrollIntoView({ behavior: 'smooth' }), 100)
        }}
      />

      <SupplementDialog applicationId={applicationId} open={supOpen} onOpenChange={setSupOpen} />
      <ApproveDialog applicationId={applicationId} open={apOpen} onOpenChange={setApOpen} />
      <RejectDialog applicationId={applicationId} open={rjOpen} onOpenChange={setRjOpen} />
    </div>
  )
}
