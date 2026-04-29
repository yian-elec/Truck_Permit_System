import { StatusBadge, InfoRow } from '@/shared/ui'

type Props = {
  status: string
  mapVersion: string
  planningVersion: string
  selectedCandidateId: string | null | undefined
  originText?: string | null
  destinationText?: string | null
}

export function RoutePlanPanel({
  status,
  mapVersion,
  planningVersion,
  selectedCandidateId,
  originText,
  destinationText,
}: Props) {
  const ot = originText?.trim()
  const dt = destinationText?.trim()
  const showEnds = !!(ot || dt)

  return (
    <div className="space-y-3 text-sm">
      <div className="flex flex-wrap items-center gap-3">
        <StatusBadge status={status} />
        <span className="text-muted-foreground">圖資版本：{mapVersion}</span>
        <span className="text-muted-foreground">規劃版本：{planningVersion}</span>
        {selectedCandidateId ? (
          <span className="font-mono text-xs">已選候選：{selectedCandidateId}</span>
        ) : null}
      </div>
      {showEnds ? (
        <div className="border-border rounded-md border bg-muted/20 px-3 py-2">
          <p className="text-muted-foreground mb-1.5 text-xs font-medium">路線申請起迄（申請人填寫）</p>
          <div className="grid gap-2 sm:grid-cols-2">
            <InfoRow label="起始點">{ot || '—'}</InfoRow>
            <InfoRow label="到達點">{dt || '—'}</InfoRow>
          </div>
        </div>
      ) : null}
    </div>
  )
}
