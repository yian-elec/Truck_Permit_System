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

function candidateLabel(c: Record<string, unknown>): string {
  const rank = c.candidate_rank ?? '?'
  const dist = c.distance_m ?? ''
  const dur = c.duration_s ?? ''
  const summary = String(c.summary_text ?? '').trim()
  const sumShort = summary.length > 160 ? `${summary.slice(0, 157)}…` : summary
  return `第 ${rank} 順位 · ${dist} m · ${dur} s${sumShort ? ` — ${sumShort}` : ''}`
}

/** 強化 datetime-local 右上角日曆圖示可點範圍，並避免父層裁切 stacking 導致點不到（含與對話框關閉鈕重疊） */
const datetimeLocalInputClass =
  'relative z-10 min-h-9 min-w-0 px-3 py-1 text-base sm:h-9 sm:text-sm [&:focus]:z-[11] [&:focus-visible]:z-[11] pr-14 ' +
  '[&::-webkit-calendar-picker-indicator]:mt-[-2px] [&::-webkit-calendar-picker-indicator]:cursor-pointer ' +
  '[&::-webkit-calendar-picker-indicator]:opacity-90 [&::-webkit-datetime-edit-text]:grow-0'

export function ApproveDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [confirmStep, setConfirmStep] = useState(false)
  const [reason, setReason] = useState('')
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')

  const planQuery = useQuery({
    queryKey: queryKeys.review.routePlan(applicationId),
    queryFn: () => getRoutePlan(applicationId),
    enabled: open && Boolean(applicationId),
  })

  const plan = planQuery.data as Record<string, unknown> | null | undefined
  const candidates = (plan?.candidates ?? []) as Record<string, unknown>[]
  const selectedRaw = plan?.selected_candidate_id ?? plan?.['selected_candidate_id']
  const selectedId = selectedRaw != null && selectedRaw !== '' ? String(selectedRaw) : ''

  const boundCandidate =
    selectedId && candidates.length > 0
      ? candidates.find((c) => String(c.candidate_id ?? '') === selectedId) ?? null
      : null

  useEffect(() => {
    if (!open) {
      setConfirmStep(false)
    }
  }, [open])

  const mutation = useMutation({
    mutationFn: () => {
      if (!selectedId) {
        throw new Error('請先在「路線審查」頁選定一條候選路線，再來核准。')
      }
      if (!boundCandidate) {
        throw new Error('找不到已選定的候選路線，請重新整理或至路線審查確認。')
      }
      return approveApplication(applicationId, {
        reason,
        approved_start_at: start ? new Date(start).toISOString() : null,
        approved_end_at: end ? new Date(end).toISOString() : null,
        selected_candidate_id: selectedId,
        override_id: null,
      })
    },
    onSuccess: async () => {
      toast.success('已核准')
      setConfirmStep(false)
      onOpenChange(false)
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.caseDetail(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.tasks })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.decisions(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.routePlan(applicationId) })
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : ApiError.fromUnknown(e).message),
  })

  const canProceed =
    Boolean(planQuery.data) &&
    !planQuery.isLoading &&
    !planQuery.isError &&
    Boolean(selectedId) &&
    Boolean(boundCandidate)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/*
        外層避免 overflow:hidden 裁切瀏覽器內建的 datetime picker。
        Radix Dialog 關閉鈕在右上角：日期列右側多留空白，並用 z-[1]／input 強化 layering，避免遮擋可點區。
      */}
      <DialogContent className="gap-4 overflow-visible p-6">
        <DialogHeader className="shrink-0 pr-8">
          <DialogTitle>核准</DialogTitle>
          <DialogDescription>
            {confirmStep
              ? '請再次確認。核准後系統會通知申請人，案件狀態將變為「已核准」。'
              : '填寫核准內容並確認時間區間（路線採你在路線審查選定的那一條），再進入確認步驟。'}
          </DialogDescription>
        </DialogHeader>
        {confirmStep ? (
          <div className="space-y-4">
            <div className="rounded-md border border-border bg-muted/40 p-4 text-sm">
              <p className="font-medium text-foreground">確定核准這件申請？</p>
              <p className="text-muted-foreground mt-2 text-xs">
                核准後，申請人會收到通知，案件狀態會變成「已核准」。
              </p>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={() => setConfirmStep(false)}
                disabled={mutation.isPending}
              >
                取消
              </Button>
              <Button type="button" loading={mutation.isPending} onClick={() => mutation.mutate()}>
                確定核准
              </Button>
            </div>
          </div>
        ) : (
          <div className="max-h-[min(70vh,calc(100vh-12rem))] space-y-3 overflow-x-visible overflow-y-auto pr-3">
            <div>
              <label className="text-muted-foreground text-xs font-medium">理由</label>
              <textarea
                className="border-input bg-background mt-1 flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>

            <div className="grid min-w-0 gap-4 sm:grid-cols-2">
              <div className="min-w-0">
                <label className="text-muted-foreground text-xs font-medium">核准起</label>
                <Input
                  type="datetime-local"
                  value={start}
                  onChange={(e) => setStart(e.target.value)}
                  className={cn(datetimeLocalInputClass, 'mt-1 block w-full')}
                />
              </div>
              <div className="min-w-0 sm:pr-2">
                <label className="text-muted-foreground text-xs font-medium">核准迄</label>
                <Input
                  type="datetime-local"
                  value={end}
                  onChange={(e) => setEnd(e.target.value)}
                  className={cn(datetimeLocalInputClass, 'mt-1 block w-full')}
                />
              </div>
            </div>

            {planQuery.isLoading ? (
              <p className="text-muted-foreground text-sm">載入路線資料…</p>
            ) : planQuery.isError ? (
              <p className="text-destructive text-sm">無法載入路線規劃，請稍後再試或至路線審查頁確認。</p>
            ) : !plan ? (
              <p className="text-muted-foreground text-sm">
                尚無路線規劃資料；若需核准請先執行自動規劃，並於路線審查選定候選路線。
              </p>
            ) : !selectedId || !boundCandidate ? (
              <p className="text-destructive text-sm">
                尚未綁定路線：請先至「路線審查」於候選路線中按「選定此路線」，再回來核准。
              </p>
            ) : (
              <div className="bg-muted/30 border-border rounded-md border px-3 py-2 text-sm">
                <p className="text-muted-foreground text-xs font-medium">核准綁定路線（已選定）</p>
                <p className="text-foreground mt-1 break-words">{candidateLabel(boundCandidate)}</p>
              </div>
            )}

            <Button
              type="button"
              className="w-full"
              onClick={() => setConfirmStep(true)}
              disabled={planQuery.isLoading || !canProceed}
            >
              下一步：確認核准
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
