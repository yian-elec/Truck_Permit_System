function statusLabel(status: string | undefined): string {
  const s = (status ?? 'open').toLowerCase()
  if (s === 'open') return '待回覆'
  if (s === 'fulfilled') return '已完成'
  if (s === 'cancelled') return '已取消'
  return status ?? '—'
}

export function SupplementRequestList({ data }: { data: unknown }) {
  const d = data as {
    items?: {
      request_id: string
      title: string
      description?: string | null
      status?: string
      created_at: string
    }[]
  }
  const items = d?.items ?? []
  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">尚無補件通知。</p>
  }

  return (
    <ul className="space-y-3">
      {items.map((it) => (
        <li key={it.request_id} className="rounded-md border border-border p-3 text-sm">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="font-medium">{it.title}</div>
            <span className="shrink-0 rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">
              {statusLabel(it.status)}
            </span>
          </div>
          {it.description ? <p className="mt-1 text-muted-foreground">{it.description}</p> : null}
          <p className="mt-2 text-xs text-muted-foreground">{it.created_at}</p>
        </li>
      ))}
    </ul>
  )
}
