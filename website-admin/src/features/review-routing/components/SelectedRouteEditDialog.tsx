import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { Button, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, Input } from '@/shared/ui'

import { patchSelectedItinerary } from '../api/route-api'
import {
  mergeConsecutiveSameRoadLabel,
  roadLabel,
  sortSegments,
  type ItineraryRow,
} from '../utils/itinerary-merge'

type RowRecord = Record<string, unknown>

type Props = {
  applicationId: string
  open: boolean
  onOpenChange: (open: boolean) => void
  candidates: RowRecord[]
  selectedId?: string | null
}

type EditRow = { localId: string; road_name: string; distance_m: number; duration_s: number }

function newLocalId(): string {
  return typeof crypto !== 'undefined' && crypto.randomUUID
    ? `r-${crypto.randomUUID()}`
    : `r-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function mergedRowsFromCandidate(cand: RowRecord): EditRow[] {
  const raw = sortSegments((cand.segments ?? []) as ItineraryRow[])
  if (raw.length === 0) return []
  const merged = mergeConsecutiveSameRoadLabel(raw)
  return merged.map((seg) => ({
    localId: newLocalId(),
    road_name:
      seg.road_name != null && String(seg.road_name).trim() !== ''
        ? String(seg.road_name).trim()
        : roadLabel(seg) === '—'
          ? ''
          : roadLabel(seg),
    distance_m: Math.max(0, Math.round(Number(seg.distance_m ?? 0))),
    duration_s: Math.max(0, Math.round(Number(seg.duration_s ?? 0))),
  }))
}

export function SelectedRouteEditDialog({ applicationId, open, onOpenChange, candidates, selectedId }: Props) {
  const queryClient = useQueryClient()
  const [rows, setRows] = useState<EditRow[]>([])

  const cand = candidates.find((c) => String(c.candidate_id ?? '') === selectedId)

  useEffect(() => {
    if (!open || !selectedId || !cand) {
      return
    }
    const next = mergedRowsFromCandidate(cand)
    setRows(next.length > 0 ? next : [{ localId: newLocalId(), road_name: '', distance_m: 100, duration_s: 10 }])
  }, [open, selectedId, cand])

  const mutation = useMutation({
    mutationFn: () => {
      const total = rows.reduce((s, r) => s + Math.max(0, r.distance_m), 0)
      if (total <= 0) {
        throw new Error('請至少設定一段距離大於 0（distance_m 總和須為正）。')
      }
      return patchSelectedItinerary(applicationId, {
        segments: rows.map((r) => ({
          road_name: r.road_name.trim() || null,
          distance_m: Math.max(0, Math.round(r.distance_m)),
          duration_s: Math.max(0, Math.round(r.duration_s)),
        })),
      })
    },
    onSuccess: async () => {
      toast.success('已儲存已選路線')
      onOpenChange(false)
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.routePlan(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.ruleHits(applicationId) })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  const canSave = rows.length >= 1 && rows.reduce((s, r) => s + Math.max(0, r.distance_m), 0) > 0

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle>調整已選路線</DialogTitle>
          <DialogDescription>
            編輯路名、距離與時間；可在任兩列之間插入新路段（距離將依比例切分總里程；儲存後即寫入後端）。
          </DialogDescription>
        </DialogHeader>
        {!selectedId || !cand ? (
          <p className="text-muted-foreground text-sm">請先選定一條候選路線。</p>
        ) : (
          <div className="space-y-3">
            <div className="text-muted-foreground grid grid-cols-[minmax(0,1fr)_90px_90px_auto] gap-2 text-xs font-medium">
              <span>道路／路段</span>
              <span>距離 (m)</span>
              <span>時間 (s)</span>
              <span className="text-right">操作</span>
            </div>
            {rows.map((r, idx) => (
              <div
                key={r.localId}
                className="border-border grid grid-cols-1 gap-2 rounded-md border p-3 sm:grid-cols-[minmax(0,1fr)_90px_90px_auto] sm:items-center sm:gap-2"
              >
                <Input
                  className="w-full min-w-0"
                  placeholder="道路名稱"
                  value={r.road_name}
                  onChange={(e) => {
                    const v = e.target.value
                    setRows((prev) =>
                      prev.map((x, i) => (i === idx ? { ...x, road_name: v } : x)),
                    )
                  }}
                />
                <Input
                  type="number"
                  min={0}
                  step={1}
                  className="font-mono"
                  value={r.distance_m === 0 ? '' : String(r.distance_m)}
                  onChange={(e) => {
                    const n = Number(e.target.value)
                    setRows((prev) =>
                      prev.map((x, i) => (i === idx ? { ...x, distance_m: Number.isFinite(n) ? n : 0 } : x)),
                    )
                  }}
                />
                <Input
                  type="number"
                  min={0}
                  step={1}
                  className="font-mono"
                  value={r.duration_s === 0 ? '' : String(r.duration_s)}
                  onChange={(e) => {
                    const n = Number(e.target.value)
                    setRows((prev) =>
                      prev.map((x, i) => (i === idx ? { ...x, duration_s: Number.isFinite(n) ? n : 0 } : x)),
                    )
                  }}
                />
                <div className="flex flex-wrap justify-end gap-1">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      setRows((prev) => {
                        const n = [...prev]
                        n.splice(idx + 1, 0, {
                          localId: newLocalId(),
                          road_name: '',
                          distance_m: 100,
                          duration_s: 10,
                        })
                        return n
                      })
                    }
                  >
                    下方插入
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    disabled={rows.length <= 1}
                    onClick={() => setRows((prev) => (prev.length <= 1 ? prev : prev.filter((_, i) => i !== idx)))}
                  >
                    刪除
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            取消
          </Button>
          <Button
            type="button"
            loading={mutation.isPending}
            disabled={!selectedId || !cand || !canSave}
            onClick={() => mutation.mutate()}
          >
            儲存
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
