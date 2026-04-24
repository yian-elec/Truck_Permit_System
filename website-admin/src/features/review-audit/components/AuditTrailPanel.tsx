import { formatDate } from '@/shared/utils/format-date'

import type { AuditEntry } from '../api/review-audit-api'

function PayloadRow({ label, value }: { label: string; value: unknown }) {
  if (value == null || value === '') return null
  const display = typeof value === 'object' ? JSON.stringify(value) : String(value)
  return (
    <div className="flex gap-2 text-xs">
      <span className="shrink-0 font-medium text-foreground capitalize min-w-[8rem]">
        {label.replace(/_/g, ' ')}
      </span>
      <span className="text-muted-foreground break-all">{display}</span>
    </div>
  )
}

export function AuditTrailPanel({ entries }: { entries: AuditEntry[] }) {
  if (entries.length === 0) {
    return <p className="text-muted-foreground text-sm">尚無稽核事件</p>
  }
  return (
    <ul className="space-y-3">
      {entries.map((e, i) => (
        <li
          key={`${e.entry_type}-${e.occurred_at}-${i}`}
          className="rounded-xl border border-border bg-muted/30 p-4"
        >
          <div className="flex flex-wrap items-center gap-3 mb-3">
            <span className="rounded-md bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
              {e.entry_type}
            </span>
            <span className="text-xs text-muted-foreground">{formatDate(e.occurred_at)}</span>
          </div>
          {e.payload && typeof e.payload === 'object' && Object.keys(e.payload).length > 0 ? (
            <div className="space-y-1.5">
              {Object.entries(e.payload as Record<string, unknown>).map(([k, v]) => (
                <PayloadRow key={k} label={k} value={v} />
              ))}
            </div>
          ) : null}
        </li>
      ))}
    </ul>
  )
}
