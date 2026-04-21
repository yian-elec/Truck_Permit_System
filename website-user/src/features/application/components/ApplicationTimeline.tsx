import type { TimelinePayload } from '../api/get-timeline'

export function ApplicationTimeline({ timeline }: { timeline: TimelinePayload }) {
  const events = timeline.events ?? (Array.isArray((timeline as { items?: unknown[] }).items) ? (timeline as { items: unknown[] }).items : [])

  if (!events.length) {
    return <p className="text-sm text-muted-foreground">尚無歷程紀錄。</p>
  }

  return (
    <ul className="space-y-3 border-l border-border pl-4">
      {events.map((ev, i) => (
        <li key={i} className="text-sm">
          <span className="font-medium">
            {typeof ev === 'object' && ev && 'message' in ev ? String((ev as { message?: string }).message) : JSON.stringify(ev)}
          </span>
        </li>
      ))}
    </ul>
  )
}
