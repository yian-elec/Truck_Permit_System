import { formatDate } from '@/shared/utils/format-date'

type Row = Record<string, unknown>

export function CommentList({ comments }: { comments: Row[] }) {
  if (comments.length === 0) {
    return <p className="text-muted-foreground text-sm">尚無評論</p>
  }
  return (
    <ul className="space-y-3">
      {comments.map((c, idx) => (
        <li key={String(c.comment_id ?? idx)} className="border-border rounded-md border p-3 text-sm">
          <div className="text-muted-foreground flex flex-wrap gap-2 text-xs">
            <span className="font-medium">{String(c.comment_type ?? '')}</span>
            <span>{c.created_at ? formatDate(String(c.created_at)) : ''}</span>
            <span className="font-mono">{String(c.created_by ?? '')}</span>
          </div>
          <p className="mt-2 whitespace-pre-wrap">{String(c.content ?? '')}</p>
        </li>
      ))}
    </ul>
  )
}
