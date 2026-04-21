import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'
import { EmptyState } from '@/shared/ui'
import { JsonPreview } from '@/shared/ui'

import { getOcrSummary } from '../api/review-ocr-api'

export function OcrSummaryPanel({ applicationId }: { applicationId: string }) {
  const q = useQuery({
    queryKey: queryKeys.review.ocrSummary(applicationId),
    queryFn: () => getOcrSummary(applicationId),
  })

  if (q.isLoading) return <p className="text-muted-foreground text-sm">載入 OCR…</p>
  if (q.isError) return <p className="text-destructive text-sm">無法載入 OCR 摘要</p>

  const summary = q.data?.ocr_summary ?? {}
  if (Object.keys(summary).length === 0) {
    return <EmptyState title="尚無 OCR 資料" />
  }
  return <JsonPreview value={summary} />
}
