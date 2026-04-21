import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { getRoutePlan } from '@/features/review-routing/api/route-api'
import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { cn } from '@/shared/lib/cn'
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Input,
} from '@/shared/ui'

import { approveApplication } from '../api/review-decision-api'

type Props = {
  applicationId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

type RouteBinding = 'candidate' | 'override'

const selectClassName = cn(
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
  'disabled:cursor-not-allowed disabled:opacity-50',
)

function candidateLabel(c: Record<string, unknown>): string {
  const rank = c.candidate_rank ?? '?'
  const dist = c.distance_m ?? ''
  const dur = c.duration_s ?? ''
  const summary = String(c.summary_text ?? '').trim()
  const sumShort = summary.length > 72 ? `${summary.slice(0, 69)}…` : summary
  return `第 ${rank} 順位 · ${dist}m · ${dur}s${sumShort ? ` · ${sumShort}` : ''}`
}

function overrideLabel(o: Record<string, unknown>): string {
  const created = o.created_at ? String(o.created_at).replace('T', ' ').slice(0, 19) : ''
  const reason = String(o.override_reason ?? '').trim()
  const reasonShort = reason.length > 100 ? `${reason.slice(0, 97)}…` : reason
  return `${created ? `${created} · ` : ''}${reasonShort || '人工改線'}`
}

export function ApproveDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [reason, setReason] = useState('')
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [routeBinding, setRouteBinding] = useState<RouteBinding>('candidate')
  const [selectedCandidateId, setSelectedCandidateId] = useState('')
  const [selectedOverrideId, setSelectedOverrideId] = useState('')

  const planQuery = useQuery({
    queryKey: queryKeys.review.routePlan(applicationId),
    queryFn: () => getRoutePlan(applicationId),
    enabled: open && Boolean(applicationId),
  })

  const plan = planQuery.data
  const candidates = (plan?.candidates ?? []) as Record<string, unknown>[]
  const overrides = (plan?.officer_overrides ?? []) as Record<string, unknown>[]

  useEffect(() => {
    if (!open || !plan) return
    const candList = (plan.candidates ?? []) as Record<string, unknown>[]
    const ovList = (plan.officer_overrides ?? plan['officer_overrides'] ?? []) as Record<string, unknown>[]
    const sel = plan.selected_candidate_id ?? plan['selected_candidate_id']
    const selStr = sel != null ? String(sel) : ''

    if (candList.length > 0 && ovList.length === 0) {
      setRouteBinding('candidate')
    } else if (candList.length === 0 && ovList.length > 0) {
      setRouteBinding('override')
    } else if (selStr && candList.some((c) => String(c.candidate_id ?? '') === selStr)) {
      setRouteBinding('candidate')
    } else if (ovList.length > 0) {
      setRouteBinding('override')
    }

    if (selStr && candList.some((c) => String(c.candidate_id ?? '') === selStr)) {
      setSelectedCandidateId(selStr)
    } else if (candList[0]?.candidate_id) {
      setSelectedCandidateId(String(candList[0].candidate_id))
    } else {
      setSelectedCandidateId('')
    }

    const firstOv = ovList[0]?.override_id
    setSelectedOverrideId(firstOv != null ? String(firstOv) : '')
  }, [open, plan])

  const mutation = useMutation({
    mutationFn: () => {
      if (routeBinding === 'candidate') {
        if (!selectedCandidateId) {
          throw new Error('請選擇一筆候選路線')
        }
        return approveApplication(applicationId, {
          reason,
          approved_start_at: start ? new Date(start).toISOString() : null,
          approved_end_at: end ? new Date(end).toISOString() : null,
          selected_candidate_id: selectedCandidateId,
          override_id: null,
        })
      }
      if (!selectedOverrideId) {
        throw new Error('請選擇一筆人工改線紀錄')
      }
      return approveApplication(applicationId, {
        reason,
        approved_start_at: start ? new Date(start).toISOString() : null,
        approved_end_at: end ? new Date(end).toISOString() : null,
        selected_candidate_id: null,
        override_id: selectedOverrideId,
      })
    },
    onSuccess: async () => {
      toast.success('已核准')
      onOpenChange(false)
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.caseDetail(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.tasks })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.decisions(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.routePlan(applicationId) })
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : ApiError.fromUnknown(e).message),
  })

  const candidateOptions = candidates
    .filter((c) => c.candidate_id != null)
    .map((c) => ({
      value: String(c.candidate_id),
      label: candidateLabel(c),
    }))

  const overrideOptions = overrides
    .filter((o) => o.override_id != null)
    .map((o) => ({
      value: String(o.override_id),
      label: overrideLabel(o),
    }))

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>核准</DialogTitle>
          <DialogDescription>核准申請並可指定許可期間與綁定之路線（候選或人工改線擇一）。</DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-muted-foreground text-xs font-medium">理由</label>
            <textarea
              className="border-input bg-background mt-1 flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="text-muted-foreground text-xs font-medium">核准起</label>
              <Input type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} />
            </div>
            <div>
              <label className="text-muted-foreground text-xs font-medium">核准迄</label>
              <Input type="datetime-local" value={end} onChange={(e) => setEnd(e.target.value)} />
            </div>
          </div>

          {planQuery.isLoading ? (
            <p className="text-muted-foreground text-sm">載入路線資料…</p>
          ) : planQuery.isError ? (
            <p className="text-destructive text-sm">無法載入路線規劃，請稍後再試或至路線審查頁確認。</p>
          ) : !plan ? (
            <p className="text-muted-foreground text-sm">尚無路線規劃資料；若需綁定路線請先執行規劃或人工改線。</p>
          ) : (
            <>
              <div className="space-y-2">
                <span className="text-sm font-medium">核准綁定路線</span>
                <p className="text-muted-foreground text-xs">
                  請擇一：以自動規劃候選為準，或以人工改線紀錄為準（不可同時指定兩者）。
                </p>
                <div className="flex flex-wrap gap-4">
                  <label className="flex cursor-pointer items-center gap-2 text-sm">
                    <input
                      type="radio"
                      className="h-4 w-4"
                      checked={routeBinding === 'candidate'}
                      disabled={candidateOptions.length === 0}
                      onChange={() => setRouteBinding('candidate')}
                    />
                    使用候選路線
                  </label>
                  <label className="flex cursor-pointer items-center gap-2 text-sm">
                    <input
                      type="radio"
                      className="h-4 w-4"
                      checked={routeBinding === 'override'}
                      disabled={overrideOptions.length === 0}
                      onChange={() => setRouteBinding('override')}
                    />
                    使用人工改線
                  </label>
                </div>
              </div>

              {routeBinding === 'candidate' ? (
                <div>
                  <label className="text-muted-foreground text-xs font-medium">候選路線</label>
                  {candidateOptions.length === 0 ? (
                    <p className="text-muted-foreground mt-1 text-sm">目前無候選路線可選。</p>
                  ) : (
                    <select
                      className={cn(selectClassName, 'mt-1')}
                      value={selectedCandidateId}
                      onChange={(e) => setSelectedCandidateId(e.target.value)}
                    >
                      <option value="" disabled>
                        請選擇候選路線
                      </option>
                      {candidateOptions.map((o) => (
                        <option key={o.value} value={o.value}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              ) : (
                <div>
                  <label className="text-muted-foreground text-xs font-medium">人工改線紀錄</label>
                  {overrideOptions.length === 0 ? (
                    <p className="text-muted-foreground mt-1 text-sm">尚無人工改線紀錄；請先於路線審查執行「人工改線」。</p>
                  ) : (
                    <select
                      className={cn(selectClassName, 'mt-1')}
                      value={selectedOverrideId}
                      onChange={(e) => setSelectedOverrideId(e.target.value)}
                    >
                      <option value="" disabled>
                        請選擇改線紀錄
                      </option>
                      {overrideOptions.map((o) => (
                        <option key={o.value} value={o.value}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
            </>
          )}

          <Button type="button" className="w-full" loading={mutation.isPending} onClick={() => mutation.mutate()}>
            確認核准
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
