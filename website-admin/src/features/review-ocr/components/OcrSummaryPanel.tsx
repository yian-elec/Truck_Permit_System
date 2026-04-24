import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'
import { EmptyState } from '@/shared/ui'

import { getOcrSummary } from '../api/review-ocr-api'

function OcrField({ label, value }: { label: string; value: unknown }) {
  const display = value == null || value === '' ? '—' : String(value)
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs font-medium text-muted-foreground capitalize">
        {label.replace(/_/g, ' ')}
      </span>
      <span className="text-sm text-foreground">{display}</span>
    </div>
  )
}

export function OcrSummaryPanel({ applicationId }: { applicationId: string }) {
  const q = useQuery({
    queryKey: queryKeys.review.ocrSummary(applicationId),
    queryFn: () => getOcrSummary(applicationId),
  })

  if (q.isLoading) return <p className="text-muted-foreground text-sm">載入中…</p>
  if (q.isError) return <p className="text-destructive text-sm">無法載入 OCR 摘要</p>

  const summary = q.data?.ocr_summary ?? {}
  if (Object.keys(summary).length === 0) {
    return <EmptyState title="尚無 OCR 辨識資料" />
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {Object.entries(summary).map(([k, v]) => (
        <OcrField key={k} label={k} value={v} />
      ))}
    </div>
  )
}
