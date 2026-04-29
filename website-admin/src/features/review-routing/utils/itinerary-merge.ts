export type ItineraryRow = Record<string, unknown>

export function sortSegments(segments: ItineraryRow[]): ItineraryRow[] {
  return [...segments].sort((a, b) => Number(a.seq_no ?? 0) - Number(b.seq_no ?? 0))
}

export function roadLabel(seg: ItineraryRow): string {
  const name = seg.road_name != null && String(seg.road_name).trim() !== '' ? String(seg.road_name) : ''
  if (name) return name
  const hint =
    seg.instruction_text != null && String(seg.instruction_text).trim() !== ''
      ? String(seg.instruction_text)
      : ''
  if (hint) return hint
  return '—'
}

/** 連續且「道路／路段」顯示文字相同者合併，距離與時間加總。 */
export function mergeConsecutiveSameRoadLabel(segments: ItineraryRow[]): ItineraryRow[] {
  if (segments.length === 0) return []

  const merged: ItineraryRow[] = []
  let acc: ItineraryRow = { ...segments[0] }
  let accLabel = roadLabel(segments[0])
  const accIds: string[] = [String(acc.segment_id ?? '')]

  const addNums = (a: unknown, b: unknown) => {
    const x = Number(a)
    const y = Number(b)
    return (Number.isFinite(x) ? x : 0) + (Number.isFinite(y) ? y : 0)
  }

  for (let i = 1; i < segments.length; i++) {
    const seg = segments[i]
    const label = roadLabel(seg)
    if (label === accLabel) {
      acc.distance_m = addNums(acc.distance_m, seg.distance_m)
      acc.duration_s = addNums(acc.duration_s, seg.duration_s)
      if (seg.is_exception_road === true) acc.is_exception_road = true
      accIds.push(String(seg.segment_id ?? ''))
    } else {
      merged.push({ ...acc, _merged_segment_ids: accIds.join(',') })
      acc = { ...seg }
      accLabel = label
      accIds.length = 0
      accIds.push(String(acc.segment_id ?? ''))
    }
  }
  merged.push({ ...acc, _merged_segment_ids: accIds.join(',') })

  return merged.map((r, idx) => ({ ...r, seq_no: idx }))
}
