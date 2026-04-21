import { formatDate } from '@/shared/utils/format-date'
import { JsonPreview } from '@/shared/ui'

import type { AuditEntry } from '../api/review-audit-api'

export function AuditTrailPanel({ entries }: { entries: AuditEntry[] }) {
  if (entries.length === 0) {
    return <p className="text-muted-foreground text-sm">尚無稽核事件</p>
  }
  return (
    <ul className="space-y-4">
      {entries.map((e, i) => (
        <li key={`${e.entry_type}-${e.occurred_at}-${i}`} className="border-border rounded-md border p-3">
          <div className="flex flex-wrap gap-2 text-sm font-medium">
            <span>{e.entry_type}</span>
            <span className="text-muted-foreground font-normal">{formatDate(e.occurred_at)}</span>
          </div>
          <div className="mt-2">
            <JsonPreview value={e.payload} />
          </div>
        </li>
      ))}
    </ul>
  )
}
