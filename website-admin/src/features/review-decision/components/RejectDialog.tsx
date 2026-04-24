import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { REJECT_REASON_PRESETS } from '@/shared/utils/admin-operator-copy'
import { Button, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/shared/ui'

import { rejectApplication } from '../api/review-decision-api'

type Props = {
  applicationId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

const selectClassName =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring'

export function RejectDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [confirmStep, setConfirmStep] = useState(false)
  const [category, setCategory] = useState('')
  const [detail, setDetail] = useState('')

  useEffect(() => {
    if (!open) {
      setConfirmStep(false)
      setCategory('')
      setDetail('')
    }
  }, [open])

  const buildReason = (): string => {
    if (!category) throw new Error('請選擇駁回原因')
    if (category === 'other' && !detail.trim()) {
      throw new Error('選擇「其他」時請填寫說明')
    }
    const label = REJECT_REASON_PRESETS.find((p) => p.value === category)?.label ?? category
    if (category === 'other') {
      return `其他：${detail.trim()}`
    }
    return detail.trim() ? `${label}。${detail.trim()}` : label
  }

  const mutation = useMutation({
    mutationFn: () => rejectApplication(applicationId, { reason: buildReason() }),
    onSuccess: async () => {
      toast.success('已駁回')
      setConfirmStep(false)
      onOpenChange(false)
      setCategory('')
      setDetail('')
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.caseDetail(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.tasks })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.decisions(applicationId) })
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : ApiError.fromUnknown(e).message),
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>駁回</DialogTitle>
          <DialogDescription>
            {confirmStep
              ? '駁回後申請人會收到通知，案件將結案為駁回。請確認原因正確。'
              : '請必須選擇原因，必要時可補充說明。'}
          </DialogDescription>
        </DialogHeader>
        {confirmStep ? (
          <div className="space-y-4">
            <div className="rounded-md border border-destructive/30 bg-destructive/5 p-4 text-sm">
              <p className="font-medium text-foreground">確定駁回此件申請？</p>
              <p className="text-muted-foreground mt-2 whitespace-pre-wrap text-xs">{buildReason()}</p>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
              <Button type="button" variant="outline" onClick={() => setConfirmStep(false)} disabled={mutation.isPending}>
                返回修改
              </Button>
              <Button type="button" variant="destructive" loading={mutation.isPending} onClick={() => mutation.mutate()}>
                確定駁回
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="text-muted-foreground text-xs font-medium">請選擇駁回原因</label>
              <select className={selectClassName} value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">—</option>
                {REJECT_REASON_PRESETS.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-muted-foreground text-xs font-medium">補充說明</label>
              <textarea
                className="border-input bg-background mt-1 flex min-h-[100px] w-full rounded-md border px-3 py-2 text-sm"
                value={detail}
                onChange={(e) => setDetail(e.target.value)}
                placeholder="可補充細節；選擇「其他」時此欄為必填。"
              />
            </div>
            <Button
              type="button"
              variant="destructive"
              className="w-full"
              onClick={() => {
                try {
                  buildReason()
                  setConfirmStep(true)
                } catch (e) {
                  toast.error(e instanceof Error ? e.message : '請完成必填欄位')
                }
              }}
            >
              下一步：確認駁回
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
