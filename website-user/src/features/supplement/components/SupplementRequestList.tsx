export function SupplementRequestList({ data }: { data: unknown }) {
  const d = data as { items?: { request_id: string; title: string; description?: string | null; created_at: string }[] }
  const items = d?.items ?? []
  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">尚無補件通知。</p>
  }

  return (
    <ul className="space-y-3">
      {items.map((it) => (
        <li key={it.request_id} className="rounded-md border border-border p-3 text-sm">
          <div className="font-medium">{it.title}</div>
          {it.description ? <p className="mt-1 text-muted-foreground">{it.description}</p> : null}
          <p className="mt-2 text-xs text-muted-foreground">{it.created_at}</p>
        </li>
      ))}
    </ul>
  )
}
