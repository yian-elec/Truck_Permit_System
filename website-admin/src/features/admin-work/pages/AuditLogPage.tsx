import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'
import { formatAuditActionForList } from '@/shared/utils/admin-operator-copy'
import { formatDate } from '@/shared/utils/format-date'
import { DataTable, type DataTableColumn, SectionCard } from '@/shared/ui'

import { listAuditLogs } from '@/features/admin-ops/api/ops-api'

type Row = Record<string, unknown>

const auditCols: DataTableColumn<Row>[] = [
  { id: 'id', header: '紀錄編號', cell: (r) => <span className="font-mono text-xs">{String(r.audit_log_id ?? r.id ?? '')}</span> },
  {
    id: 'at',
    header: '操作者',
    cell: (r) => {
      const t = String(r.actor_type ?? '').toLowerCase()
      if (t === 'system' || t === 'service') return '系統'
      if (t === 'user' || t === 'admin') return '後台人員'
      return String(r.actor_type ?? '') || '—'
    },
  },
  {
    id: 'ac',
    header: '操作',
    cell: (r) => {
      const raw = String(r.action_code ?? '')
      return (
        <span className="text-sm" title={raw || undefined}>
          {formatAuditActionForList(raw || undefined)}
        </span>
      )
    },
  },
  { id: 'rt', header: '對象', cell: (r) => String(r.resource_type ?? '') },
  { id: 'ca', header: '時間', cell: (r) => (r.created_at ? formatDate(String(r.created_at)) : '—') },
]

export function AuditLogPage() {
  const q = useQuery({ queryKey: queryKeys.ops.auditLogs, queryFn: listAuditLogs })

  return (
    <div className="space-y-4">
      <SectionCard title="操作紀錄">
        <p className="text-muted-foreground mb-4 text-sm">系統內帳號與服務所留存的稽核流水；與單一申請審核分頁無關。</p>
        {q.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : q.isError ? (
          <p className="text-destructive text-sm">無法載入操作紀錄</p>
        ) : (
          <DataTable columns={auditCols} data={q.data ?? []} getRowId={(r) => String(r.audit_log_id ?? r.id ?? '')} />
        )}
      </SectionCard>
    </div>
  )
}
