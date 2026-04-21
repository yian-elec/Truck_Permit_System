import { formatDate } from '@/shared/utils/format-date'
import { Button, DataTable, type DataTableColumn } from '@/shared/ui'

type Row = Record<string, unknown>

export function ImportJobTable({
  jobs,
  onView,
}: {
  jobs: Row[]
  onView: (id: string) => void
}) {
  const columns: DataTableColumn<Row>[] = [
    {
      id: 'id',
      header: 'import_job_id',
      cell: (r) => <span className="font-mono text-xs">{String(r.import_job_id ?? r.id ?? '')}</span>,
    },
    { id: 'status', header: 'status', cell: (r) => String(r.status ?? '') },
    {
      id: 'created',
      header: 'created_at',
      cell: (r) => (r.created_at ? formatDate(String(r.created_at)) : '—'),
    },
    {
      id: 'updated',
      header: 'updated_at',
      cell: (r) => (r.updated_at ? formatDate(String(r.updated_at)) : '—'),
    },
    {
      id: 'act',
      header: '',
      cell: (r) => {
        const id = String(r.import_job_id ?? r.id ?? '')
        return (
          <Button type="button" variant="outline" size="sm" disabled={!id} onClick={() => id && onView(id)}>
            查看作業
          </Button>
        )
      },
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={jobs}
      getRowId={(r) => String(r.import_job_id ?? r.id ?? Math.random())}
      emptyMessage="尚無匯入作業（可先送出 KML）"
    />
  )
}
