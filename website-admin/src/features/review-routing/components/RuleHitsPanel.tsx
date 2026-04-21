import { DataTable, type DataTableColumn } from '@/shared/ui'

type Row = Record<string, unknown>

export function RuleHitsPanel({ hits }: { hits: Row[] }) {
  const columns: DataTableColumn<Row>[] = [
    { id: 'rule', header: '規則 ID', cell: (r) => <span className="font-mono text-xs">{String(r.rule_id ?? '')}</span> },
    { id: 'type', header: '規則類型', cell: (r) => String(r.rule_type ?? '') },
    { id: 'hit', header: '命中類型', cell: (r) => String(r.hit_type ?? '') },
    { id: 'detail', header: '說明', cell: (r) => String(r.detail_text ?? '') },
  ]

  return (
    <DataTable
      columns={columns}
      data={hits}
      getRowId={(r) =>
        `${String(r.rule_id ?? '')}-${String(r.hit_type ?? '')}-${String(r.segment_id ?? '')}`
      }
      emptyMessage="無規則命中"
    />
  )
}
