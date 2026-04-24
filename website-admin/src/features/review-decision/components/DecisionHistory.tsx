import { formatDate } from '@/shared/utils/format-date'
import { StatusBadge } from '@/shared/ui'

type Row = Record<string, unknown>

export function DecisionHistory({ decisions }: { decisions: Row[] }) {
  if (decisions.length === 0) {
    return (
      <p className="text-muted-foreground text-sm">
        目前沒有決策紀錄。完成核准、駁回或補件要求後，會依序顯示在這裡。
      </p>
    )
  }
  return (
    <ul className="space-y-2">
      {decisions.map((d, idx) => {
        const id = String(d.decision_id ?? idx)
        return (
          <li key={id} className="border-border rounded-md border p-3 text-sm">
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge status={String(d.decision_type ?? '')} />
              <span className="text-muted-foreground text-xs">
                {d.decided_at ? formatDate(String(d.decided_at)) : ''}
              </span>
            </div>
            <p className="text-muted-foreground mt-1 text-xs font-mono">by {String(d.decided_by ?? '')}</p>
            <p className="mt-2 whitespace-pre-wrap">{String(d.reason ?? '')}</p>
          </li>
        )
      })}
    </ul>
  )
}
