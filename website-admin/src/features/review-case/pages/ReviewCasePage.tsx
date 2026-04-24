import { useQuery } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
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

import { getReviewApplication, getReviewPageModel } from '../api/review-case-api'
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

  const pageModelQuery = useQuery({
    queryKey: queryKeys.review.pageModel(applicationId),
    queryFn: () => getReviewPageModel(applicationId),
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

  return (
    <div className="space-y-4 pb-24">
      {/* 頂部摘要卡片 — 永遠顯示 */}
      <SectionCard>
        <ReviewCaseHeader application={application} />
      </SectionCard>

      {/* Tab 分頁 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full justify-start gap-1 h-auto p-1.5 flex-wrap">
          <TabsTrigger value="overview">基本資料</TabsTrigger>
          <TabsTrigger value="attachments">附件</TabsTrigger>
          <TabsTrigger value="ocr">OCR 辨識</TabsTrigger>
          <TabsTrigger value="route">路線</TabsTrigger>
          <TabsTrigger value="comments">
            評論
            {comments.length > 0 && (
              <span className="ml-1.5 rounded-full bg-primary/15 px-1.5 py-0.5 text-xs font-medium text-primary">
                {comments.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="history">決策紀錄</TabsTrigger>
          <TabsTrigger value="audit">稽核軌跡</TabsTrigger>
        </TabsList>

        {/* 基本資料 */}
        <TabsContent value="overview">
          <SectionCard title="申請資料">
            <ReviewCaseSummary application={application} />
          </SectionCard>
        </TabsContent>

        {/* 附件 */}
        <TabsContent value="attachments">
          <SectionCard title="附件文件">
            <AttachmentPreviewList applicationId={applicationId} attachments={attachments} />
          </SectionCard>
        </TabsContent>

        {/* OCR 辨識 */}
        <TabsContent value="ocr">
          <SectionCard title="OCR 辨識摘要">
            <OcrSummaryPanel applicationId={applicationId} />
          </SectionCard>
        </TabsContent>

        {/* 路線 */}
        <TabsContent value="route">
          <SectionCard title="路線資料">
            {routeSnap && Object.keys(routeSnap).length > 0 ? (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">已載入路線規劃資料。</p>
                <Link
                  className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
                  to={routePaths.reviewRoute(applicationId)}
                >
                  前往路線審查 →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">尚無路線資料。</p>
                <Link
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted transition-colors"
                  to={routePaths.reviewRoute(applicationId)}
                >
                  前往路線審查頁
                </Link>
              </div>
            )}
          </SectionCard>
        </TabsContent>

        {/* 評論 */}
        <TabsContent value="comments">
          <SectionCard title="評論與備注">
            <div ref={commentSectionRef}>
              <CommentList comments={comments} />
              <div className="mt-4 border-t border-border pt-4">
                <CommentForm applicationId={applicationId} />
              </div>
            </div>
          </SectionCard>
        </TabsContent>

        {/* 決策紀錄 */}
        <TabsContent value="history">
          <SectionCard title="決策歷史">
            <DecisionHistory decisions={decisions} />
          </SectionCard>
        </TabsContent>

        {/* 稽核軌跡 */}
        <TabsContent value="audit">
          <SectionCard title="稽核軌跡">
            {auditQuery.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : auditQuery.data ? (
              <AuditTrailPanel entries={auditQuery.data} />
            ) : (
              <p className="text-destructive text-sm">無法載入</p>
            )}
          </SectionCard>
        </TabsContent>
      </Tabs>

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
