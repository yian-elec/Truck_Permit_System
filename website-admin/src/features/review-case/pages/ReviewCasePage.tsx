import { useQuery } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { JsonPreview, SectionCard } from '@/shared/ui'

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
    return <p className="text-muted-foreground text-sm">載入案件…</p>
  }
  if (caseQuery.isError || !caseQuery.data) {
    return <p className="text-destructive text-sm">無法載入案件</p>
  }

  return (
    <div className="space-y-6 pb-24">
      <SectionCard title="案件摘要">
        <ReviewCaseHeader application={application} />
      </SectionCard>

      <SectionCard title="基本資料">
        <ReviewCaseSummary application={application} />
      </SectionCard>

      <SectionCard title="附件">
        <AttachmentPreviewList applicationId={applicationId} attachments={attachments} />
      </SectionCard>

      <SectionCard title="OCR 摘要">
        <OcrSummaryPanel applicationId={applicationId} />
      </SectionCard>

      <SectionCard title="路線摘要（聚合）">
        {routeSnap && Object.keys(routeSnap).length > 0 ? (
          import.meta.env.DEV ? (
            <JsonPreview value={routeSnap} />
          ) : (
            <p className="text-sm">
              已載入路線資料。
              <Link className="text-primary ml-2 underline" to={routePaths.reviewRoute(applicationId)}>
                前往路線審查
              </Link>
            </p>
          )
        ) : (
          <p className="text-muted-foreground text-sm">尚無路線資料（可至路線審查頁）</p>
        )}
      </SectionCard>

      <SectionCard title="評論">
        <div ref={commentSectionRef}>
          <CommentList comments={comments} />
          <div className="mt-4 border-t border-border pt-4">
            <CommentForm applicationId={applicationId} />
          </div>
        </div>
      </SectionCard>

      <SectionCard title="決策歷史">
        <DecisionHistory decisions={decisions} />
      </SectionCard>

      <SectionCard title="稽核軌跡">
        {auditQuery.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : auditQuery.data ? (
          <AuditTrailPanel entries={auditQuery.data} />
        ) : (
          <p className="text-destructive text-sm">無法載入</p>
        )}
      </SectionCard>

      {import.meta.env.DEV && pageModelQuery.data ? (
        <SectionCard title="Page model（審查契約，開發除錯）">
          <JsonPreview value={pageModelQuery.data} />
        </SectionCard>
      ) : null}

      <ReviewActionBar
        applicationId={applicationId}
        onSupplement={() => setSupOpen(true)}
        onApprove={() => setApOpen(true)}
        onReject={() => setRjOpen(true)}
        onComment={() => commentSectionRef.current?.scrollIntoView({ behavior: 'smooth' })}
      />

      <SupplementDialog applicationId={applicationId} open={supOpen} onOpenChange={setSupOpen} />
      <ApproveDialog applicationId={applicationId} open={apOpen} onOpenChange={setApOpen} />
      <RejectDialog applicationId={applicationId} open={rjOpen} onOpenChange={setRjOpen} />
    </div>
  )
}
