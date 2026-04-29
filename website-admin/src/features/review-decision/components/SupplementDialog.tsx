import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Input,
} from '@/shared/ui'

import { SUPPLEMENT_MESSAGE_TEMPLATES } from '@/shared/utils/admin-operator-copy'

import { requestSupplement } from '../api/review-decision-api'

type Props = {
  applicationId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

type Step = 'form' | 'confirm'

export function SupplementDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [title, setTitle] = useState('')
  const [message, setMessage] = useState('')
  const [deadlineAt, setDeadlineAt] = useState('')
  const [decisionReason, setDecisionReason] = useState('')
  const [step, setStep] = useState<Step>('form')

  useEffect(() => {
    if (open) {
      setTitle('')
      setMessage('')
      setDeadlineAt('')
      setDecisionReason('')
      setStep('form')
    }
  }, [open])

  function buildPayload() {
    const trimmedTitle = title.trim()
    const trimmedMessage = message.trim()
    if (!trimmedTitle) {
      throw new Error('請填寫補件標題')
    }
    if (!trimmedMessage) {
      throw new Error('請填寫給申請人的說明內容')
    }

    let deadline_at: string | null = null
    if (deadlineAt) {
      const d = new Date(deadlineAt)
      if (Number.isNaN(d.getTime())) {
        throw new Error('補件期限格式不正確')
      }
      deadline_at = d.toISOString()
    }

    const trimmedInternal = decisionReason.trim()
    const decision_reason = trimmedInternal || trimmedMessage

    return {
      title: trimmedTitle,
      message: trimmedMessage,
      deadline_at,
      decision_reason,
    }
  }

  const mutation = useMutation({
    mutationFn: () => {
      const payload = buildPayload()
      return requestSupplement(applicationId, payload)
    },
    onSuccess: async () => {
      toast.success('已發出補件')
      onOpenChange(false)
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.caseDetail(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.tasks })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.decisions(applicationId) })
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : ApiError.fromUnknown(e).message),
  })

  function goConfirm() {
    try {
      buildPayload()
      setStep('confirm')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : '請檢查表單')
    }
  }

  const trimmedTitle = title.trim()
  const trimmedMessage = message.trim()

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        if (!o) setStep('form')
        onOpenChange(o)
      }}
    >
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{step === 'form' ? '補件要求' : '確認送出補件'}</DialogTitle>
          <DialogDescription>
            {step === 'form' ? (
              <>請填寫補件標題與給申請人的說明；送出後申請人將可看到標題與完整內容。</>
            ) : (
              <>請再確認內容無誤後送出；送出後申請人將可看到補件說明與期限（若有填）。</>
            )}
          </DialogDescription>
        </DialogHeader>
        {step === 'confirm' ? (
          <div className="space-y-4">
            <div className="border-border space-y-2 rounded-md border bg-muted/30 p-3 text-sm">
              <p>
                <span className="text-muted-foreground">標題 </span>
                <span className="font-medium">{trimmedTitle}</span>
              </p>
              <div>
                <p className="text-muted-foreground text-xs">給申請人的說明</p>
                <p className="mt-1 max-h-40 overflow-y-auto whitespace-pre-wrap">{trimmedMessage}</p>
              </div>
              {deadlineAt ? (
                <p>
                  <span className="text-muted-foreground">補件期限 </span>
                  {new Date(deadlineAt).toLocaleString('zh-TW', {
                    dateStyle: 'short',
                    timeStyle: 'short',
                  })}
                </p>
              ) : (
                <p className="text-muted-foreground">未設定補件期限</p>
              )}
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
              <Button type="button" variant="outline" onClick={() => setStep('form')}>
                返回修改
              </Button>
              <Button
                type="button"
                className="sm:min-w-[7rem]"
                loading={mutation.isPending}
                onClick={() => mutation.mutate()}
              >
                確定發出補件
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="text-muted-foreground text-xs font-medium">補件標題</label>
              <Input
                className="mt-1"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="簡短標題，例如：請補上行照影本"
              />
            </div>
            <div>
              <label className="text-muted-foreground text-xs font-medium">給申請人的說明</label>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {SUPPLEMENT_MESSAGE_TEMPLATES.map((t) => (
                  <button
                    key={t}
                    type="button"
                    className="rounded-md border border-border bg-muted/50 px-2 py-1 text-left text-xs text-foreground hover:bg-muted"
                    onClick={() => setMessage((m) => (m ? `${m}\n${t}` : t))}
                  >
                    {t}
                  </button>
                ))}
              </div>
              <textarea
                className="border-input bg-background mt-2 flex min-h-[100px] w-full rounded-md border px-3 py-2 text-sm"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="補件詳細說明（必填）"
              />
            </div>
            <div>
              <label className="text-muted-foreground text-xs font-medium">補件期限</label>
              <Input
                type="datetime-local"
                value={deadlineAt}
                onChange={(e) => setDeadlineAt(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-muted-foreground text-xs font-medium">內部決策說明（選填）</label>
              <p className="text-muted-foreground mt-0.5 text-[11px] leading-snug">
                留白時將與「給申請人的說明」相同，以符合系統對內紀錄必填欄位。
              </p>
              <textarea
                className="border-input bg-background mt-1 flex min-h-[64px] w-full rounded-md border px-3 py-2 text-sm"
                value={decisionReason}
                onChange={(e) => setDecisionReason(e.target.value)}
                placeholder="可留空，會沿用給申請人的說明"
              />
            </div>
            <Button type="button" className="w-full" onClick={goConfirm}>
              下一步：確認內容
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
