import { StatusBadge } from '@/shared/ui'

type Props = {
  status: string
  mapVersion: string
  planningVersion: string
  selectedCandidateId: string | null | undefined
}

export function RoutePlanPanel({ status, mapVersion, planningVersion, selectedCandidateId }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3 text-sm">
      <StatusBadge status={status} />
      <span className="text-muted-foreground">圖資版本：{mapVersion}</span>
      <span className="text-muted-foreground">規劃版本：{planningVersion}</span>
      {selectedCandidateId ? (
        <span className="font-mono text-xs">已選候選：{selectedCandidateId}</span>
      ) : null}
    </div>
  )
}
