import { formatDate } from '@/shared/utils/format-date'
import { InfoRow, StatusBadge } from '@/shared/ui'

type Row = Record<string, unknown>

function labelSupplementStatus(raw: string): string {
  switch (raw.toLowerCase()) {
    case 'open':
      return '待申請人回覆'
    case 'fulfilled':
      return '已完成'
    case 'cancelled':
      return '已取消'
    default:
      return raw || '—'
  }
}

export function SupplementRequestRecordsPanel({ requests }: { requests: Row[] }) {
  if (requests.length === 0) {
    return (
      <p className="text-muted-foreground text-sm">尚無發出補件紀錄。</p>
    )
  }

  return (
    <div className="space-y-4">
      <p className="text-muted-foreground text-sm">
        以下為本系統登錄之每次補件要求。申請人送件後，實際修改內容與附件請至「申請內容」「文件附件」對照；若需狀態時間點，亦可參考「系統內部操作」時間軸。
      </p>
      <ul className="space-y-4">
        {requests.map((r, idx) => {
          const id = String(r.supplement_request_id ?? idx)
          const st = labelSupplementStatus(String(r.status ?? ''))
          const deadline = r.deadline_at ? formatDate(String(r.deadline_at)) : null
          const created = r.created_at ? formatDate(String(r.created_at)) : null
          const updated = r.updated_at ? formatDate(String(r.updated_at)) : null
          const title = String(r.title ?? '').trim()
          return (
            <li key={id} className="border-border rounded-lg border bg-muted/20 p-4 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge status={st} />
                {created ? (
                  <span className="text-muted-foreground text-xs tabular-nums">發出 · {created}</span>
                ) : null}
              </div>
              <p className="mt-3 text-base font-semibold text-foreground">{title || '（無標題）'}</p>
              <div className="mt-2">
                <p className="text-muted-foreground text-xs font-medium">給申請人之說明</p>
                <p className="mt-1 whitespace-pre-wrap text-foreground">{String(r.message ?? '—')}</p>
              </div>
              {(() => {
                const responded = r.responded_at ? formatDate(String(r.responded_at)) : null
                const note = String(r.applicant_response_note ?? '').trim()
                const showBlock =
                  st === '已完成' || responded || Boolean(note)
                if (!showBlock) return null
                return (
                  <div className="border-border bg-background/80 mt-3 rounded-md border px-3 py-2.5">
                    <p className="text-muted-foreground text-xs font-medium">申請人回覆</p>
                    {responded ? (
                      <p className="text-muted-foreground mt-1 text-xs tabular-nums">送出時間 · {responded}</p>
                    ) : null}
                    {note ? (
                      <p className="mt-2 whitespace-pre-wrap text-sm text-foreground">{note}</p>
                    ) : st === '已完成' ? (
                      <p className="text-muted-foreground mt-2 text-sm">（未填寫說明欄；請併同「申請內容」「文件附件」檢視實際補件）</p>
                    ) : null}
                  </div>
                )
              })()}
              <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
                <InfoRow label="補件編號">
                  <span className="break-all font-mono text-[0.7rem]">{id}</span>
                </InfoRow>
                <InfoRow label="發起人 (user id)">
                  <span className="break-all font-mono text-[0.7rem]">
                    {String(r.requested_by ?? '—')}
                  </span>
                </InfoRow>
                <InfoRow label="期限">{deadline ?? '—'}</InfoRow>
                <InfoRow label="最後更新">{updated ?? '—'}</InfoRow>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
