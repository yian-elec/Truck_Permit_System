import { DataTable, type DataTableColumn } from '@/shared/ui'

type Row = Record<string, unknown>

function sortSegments(segments: Row[]): Row[] {
  return [...segments].sort((a, b) => Number(a.seq_no ?? 0) - Number(b.seq_no ?? 0))
}

function roadLabel(seg: Row): string {
  const name = seg.road_name != null && String(seg.road_name).trim() !== '' ? String(seg.road_name) : ''
  if (name) return name
  const hint = seg.instruction_text != null && String(seg.instruction_text).trim() !== '' ? String(seg.instruction_text) : ''
  if (hint) return hint
  return '—'
}

export function SelectedRouteItinerary({
  candidates,
  selectedId,
}: {
  candidates: Row[]
  selectedId: string | null | undefined
}) {
  if (!selectedId) {
    return (
      <p className="text-muted-foreground text-sm">
        請先從下方候選路線按「選定此路線」。選定後，此處會依序列出<span className="text-foreground font-medium"> 行經道路／路段指引</span>
        （資料來自後端 <code className="text-xs">segments</code>）。
      </p>
    )
  }

  const cand = candidates.find((c) => String(c.candidate_id ?? '') === selectedId)
  if (!cand) {
    return <p className="text-destructive text-sm">找不到已選候選之路段明細。</p>
  }

  const segments = sortSegments((cand.segments ?? []) as Row[])

  if (segments.length === 0) {
    return <p className="text-muted-foreground text-sm">此候選尚無路段明細，無法列出道路。</p>
  }

  const columns: DataTableColumn<Row>[] = [
    {
      id: 'step',
      header: '順序',
      cell: (r) => String(Number(r.seq_no ?? 0) + 1),
      className: 'whitespace-nowrap w-14',
    },
    {
      id: 'road',
      header: '道路／路段',
      cell: (r) => <span className="font-medium text-foreground">{roadLabel(r)}</span>,
    },
    {
      id: 'instr',
      header: '轉向／指引',
      cell: (r) => {
        const name = r.road_name != null ? String(r.road_name).trim() : ''
        const instr = r.instruction_text != null ? String(r.instruction_text).trim() : ''
        if (instr && instr !== name) return instr
        return '—'
      },
    },
    {
      id: 'dist',
      header: '距離 (m)',
      cell: (r) => String(r.distance_m ?? '—'),
      className: 'whitespace-nowrap',
    },
    {
      id: 'dur',
      header: '時間 (s)',
      cell: (r) => String(r.duration_s ?? '—'),
      className: 'whitespace-nowrap',
    },
    {
      id: 'exc',
      header: '例外道路',
      className: 'whitespace-nowrap',
      cell: (r) => (r.is_exception_road === true ? '是' : '否'),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={segments}
      getRowId={(r) => String(r.segment_id ?? `${selectedId}-${String(r.seq_no ?? '')}`)}
      emptyMessage="無路段"
    />
  )
}
