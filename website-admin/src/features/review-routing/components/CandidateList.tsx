import { Button } from '@/shared/ui'
import { DataTable, type DataTableColumn } from '@/shared/ui'

type Row = Record<string, unknown>

export function CandidateList({
  candidates,
  selectedId,
  onSelect,
}: {
  candidates: Row[]
  selectedId: string | null | undefined
  onSelect: (candidateId: string) => void
}) {
  const columns: DataTableColumn<Row>[] = [
    {
      id: 'rank',
      header: '排序',
      cell: (r) => String(r.candidate_rank ?? ''),
    },
    {
      id: 'distance',
      header: '距離 (m)',
      cell: (r) => String(r.distance_m ?? ''),
    },
    {
      id: 'duration',
      header: '時間 (s)',
      cell: (r) => String(r.duration_s ?? ''),
    },
    {
      id: 'score',
      header: '分數',
      cell: (r) => String(r.score ?? ''),
    },
    {
      id: 'summary',
      header: '摘要',
      cell: (r) => String(r.summary_text ?? ''),
    },
    {
      id: 'action',
      header: '',
      cell: (r) => {
        const id = String(r.candidate_id ?? '')
        const isSel = selectedId === id
        return (
          <Button
            type="button"
            size="sm"
            variant={isSel ? 'secondary' : 'outline'}
            disabled={!id}
            onClick={() => id && onSelect(id)}
          >
            選定此路線
          </Button>
        )
      },
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={candidates}
      getRowId={(r) => String(r.candidate_id ?? Math.random())}
      emptyMessage="無候選路線"
    />
  )
}
