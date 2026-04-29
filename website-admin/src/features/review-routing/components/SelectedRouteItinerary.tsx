import { DataTable, type DataTableColumn } from '@/shared/ui'

import {
  mergeConsecutiveSameRoadLabel,
  roadLabel,
  sortSegments,
  type ItineraryRow,
} from '../utils/itinerary-merge'

export function SelectedRouteItinerary({
  candidates,
  selectedId,
}: {
  candidates: ItineraryRow[]
  selectedId: string | null | undefined
}) {
  if (!selectedId) {
    return (
      <p className="text-muted-foreground text-sm">
        請先從下方候選路線按「選定此路線」。選定後，此處會依序列出<span className="text-foreground font-medium"> 行經道路</span>
        （連續同名路段已合併；資料來自後端 <code className="text-xs">segments</code>）。
      </p>
    )
  }

  const cand = candidates.find((c) => String(c.candidate_id ?? '') === selectedId)
  if (!cand) {
    return <p className="text-destructive text-sm">找不到已選候選之路段明細。</p>
  }

  const rawSegments = sortSegments((cand.segments ?? []) as ItineraryRow[])

  if (rawSegments.length === 0) {
    return <p className="text-muted-foreground text-sm">此候選尚無路段明細，無法列出道路。</p>
  }

  const segments = mergeConsecutiveSameRoadLabel(rawSegments)

  const columns: DataTableColumn<ItineraryRow>[] = [
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
  ]

  return (
    <DataTable
      columns={columns}
      data={segments}
      getRowId={(r) =>
        String(r._merged_segment_ids ?? r.segment_id ?? `${selectedId}-${String(r.seq_no ?? '')}`)
      }
      emptyMessage="無路段"
    />
  )
}
