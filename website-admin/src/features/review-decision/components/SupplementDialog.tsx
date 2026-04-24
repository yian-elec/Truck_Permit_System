import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Trash2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

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

import { SUPPLEMENT_MESSAGE_TEMPLATES } from '@/shared/utils/admin-operator-copy'

import { requestSupplement } from '../api/review-decision-api'
import { SUPPLEMENT_DOCUMENT_PRESETS } from '../constants/supplement-presets'

type Props = {
  applicationId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

type SupplementRow = {
  id: string
  code: string
  note: string
}

function newRow(): SupplementRow {
  return { id: crypto.randomUUID(), code: '', note: '' }
}

const selectClassName = cn(
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
  'disabled:cursor-not-allowed disabled:opacity-50',
)

type Step = 'form' | 'confirm'

export function SupplementDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState('')
  const [deadlineAt, setDeadlineAt] = useState('')
  const [decisionReason, setDecisionReason] = useState('')
  const [rows, setRows] = useState<SupplementRow[]>([newRow()])
  const [step, setStep] = useState<Step>('form')

  useEffect(() => {
    if (open) {
      setMessage('')
      setDeadlineAt('')
      setDecisionReason('')
      setRows([newRow()])
      setStep('form')
    }
  }, [open])

  function buildPayload() {
    const selected = rows.filter((r) => r.code.trim() !== '')
    if (selected.length === 0) {
      throw new Error('請至少選擇一項補件文件')
    }
    const codes = selected.map((r) => r.code)
    if (new Set(codes).size !== codes.length) {
      throw new Error('同一文件項目不可重複，請移除多餘列')
    }
    return {
      message,
      deadline_at: deadlineAt ? new Date(deadlineAt).toISOString() : null,
      items: selected.map((r) => {
        const title = SUPPLEMENT_DOCUMENT_PRESETS.find((p) => p.code === r.code)?.title ?? r.code
        return {
          item_code: r.code,
          item_name: title,
          required_action: 'upload' as const,
          note: r.note.trim() || null,
        }
      }),
      decision_reason: decisionReason,
    }
  }

  const mutation = useMutation({
    mutationFn: () => {
      const payload = buildPayload()
      return requestSupplement(applicationId, {
        message: payload.message,
        deadline_at: payload.deadline_at,
        items: payload.items,
        decision_reason: payload.decision_reason,
      })
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

  const updateRow = (id: string, patch: Partial<Pick<SupplementRow, 'code' | 'note'>>) => {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, ...patch } : r)))
  }

  const removeRow = (id: string) => {
    setRows((prev) => {
      if (prev.length <= 1) return prev
      return prev.filter((r) => r.id !== id)
    })
  }

  const selectedRows = rows.filter((r) => r.code.trim() !== '')

  function goConfirm() {
    try {
      buildPayload()
      setStep('confirm')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : '請檢查表單')
    }
  }

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
              <>選擇須補交之文件並填寫給申請人的說明；系統會記錄為「須上傳」項目。</>
            ) : (
              <>請再確認內容無誤後送出；送出後申請人將可看到補件說明與期限（若有填）。</>
            )}
          </DialogDescription>
        </DialogHeader>
        {step === 'confirm' ? (
          <div className="space-y-4">
            <div className="space-y-2 rounded-md border border-border bg-muted/30 p-3 text-sm">
              <p>
                <span className="text-muted-foreground">補件項目 </span>
                <span className="font-medium">{selectedRows.length} 項</span>
              </p>
              <ul className="list-inside list-disc space-y-1 text-foreground">
                {selectedRows.map((r) => {
                  const title = SUPPLEMENT_DOCUMENT_PRESETS.find((p) => p.code === r.code)?.title ?? r.code
                  return <li key={r.id}>{title}</li>
                })}
              </ul>
              {deadlineAt ? (
                <p>
                  <span className="text-muted-foreground">補件期限 </span>
                  {new Date(deadlineAt).toLocaleString('zh-TW', { dateStyle: 'short', timeStyle: 'short' })}
                </p>
              ) : (
                <p className="text-muted-foreground">未設定補件期限</p>
              )}
              <div>
                <p className="text-muted-foreground text-xs">給申請人的說明</p>
                <p className="mt-1 max-h-32 overflow-y-auto whitespace-pre-wrap">{message.trim() || '（無）'}</p>
              </div>
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
        ) : null}
        {step === 'form' ? (
        <div className="space-y-3">
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
              className="border-input bg-background mt-2 flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="可點上方常用句，或自行輸入。"
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
            <textarea
              className="border-input bg-background mt-1 flex min-h-[64px] w-full rounded-md border px-3 py-2 text-sm"
              value={decisionReason}
              onChange={(e) => setDecisionReason(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">補件項目</span>
              <Button type="button" variant="outline" size="sm" onClick={() => setRows((p) => [...p, newRow()])}>
                新增項目
              </Button>
            </div>
            {rows.map((row) => (
              <div
                key={row.id}
                className="border-border space-y-2 rounded-md border p-3"
              >
                <div className="flex gap-2">
                  <div className="min-w-0 flex-1 space-y-1">
                    <label className="text-muted-foreground text-xs">文件</label>
                    <select
                      className={selectClassName}
                      value={row.code}
                      onChange={(e) => updateRow(row.id, { code: e.target.value })}
                    >
                      <option value="">請選擇文件項目</option>
                      {SUPPLEMENT_DOCUMENT_PRESETS.map((p) => (
                        <option key={p.code} value={p.code}>
                          {p.title}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex shrink-0 flex-col justify-end">
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      className="h-9 w-9"
                      disabled={rows.length <= 1}
                      title={rows.length <= 1 ? '至少保留一列' : '移除此項目'}
                      onClick={() => removeRow(row.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div>
                  <label className="text-muted-foreground text-xs">承辦備註（選填）</label>
                  <Input
                    className="mt-1"
                    placeholder="例如：請補清晰全頁、須含有效定檢日…"
                    value={row.note}
                    onChange={(e) => updateRow(row.id, { note: e.target.value })}
                  />
                </div>
              </div>
            ))}
          </div>
          <Button type="button" className="w-full" onClick={goConfirm}>
            下一步：確認內容
          </Button>
        </div>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}
