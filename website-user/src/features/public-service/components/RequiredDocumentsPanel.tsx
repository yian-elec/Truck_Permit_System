import type { RequiredDocumentsPayload } from '../types/public-service.types'

export function RequiredDocumentsPanel({ data }: { data: RequiredDocumentsPayload }) {
  return (
    <section className="rounded-lg border border-border bg-background p-6 shadow-sm">
      <h3 className="text-lg font-semibold">應備文件</h3>
      <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-muted-foreground">
        {data.documents.length === 0 ? (
          <li>尚無清單。</li>
        ) : (
          data.documents.map((d, i) => (
            <li key={d.id ?? i}>
              <span className="font-medium text-foreground">{d.title ?? '文件'}</span>
              {d.description ? ` — ${d.description}` : null}
            </li>
          ))
        )}
      </ul>
    </section>
  )
}
