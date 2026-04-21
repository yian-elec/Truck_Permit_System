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

export function SupplementDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState('')
  const [deadlineAt, setDeadlineAt] = useState('')
  const [decisionReason, setDecisionReason] = useState('')
  const [rows, setRows] = useState<SupplementRow[]>([newRow()])

  useEffect(() => {
    if (open) {
      setMessage('')
      setDeadlineAt('')
      setDecisionReason('')
      setRows([newRow()])
    }
  }, [open])

  const mutation = useMutation({
    mutationFn: () => {
      const selected = rows.filter((r) => r.code.trim() !== '')
      if (selected.length === 0) {
        throw new Error('請至少選擇一項補件文件')
      }
      const codes = selected.map((r) => r.code)
      if (new Set(codes).size !== codes.length) {
        throw new Error('同一文件項目不可重複，請移除多餘列')
      }
      return requestSupplement(applicationId, {
        message,
        deadline_at: deadlineAt ? new Date(deadlineAt).toISOString() : null,
        items: selected.map((r) => {
          const title =
            SUPPLEMENT_DOCUMENT_PRESETS.find((p) => p.code === r.code)?.title ?? r.code
          return {
            item_code: r.code,
            item_name: title,
            required_action: 'upload',
            note: r.note.trim() || null,
          }
        }),
        decision_reason: decisionReason,
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>補件</DialogTitle>
          <DialogDescription>
            選擇須補交之文件並填寫說明；系統會自動帶入代碼與「須上傳」動作。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-muted-foreground text-xs font-medium">說明 message</label>
            <textarea
              className="border-input bg-background mt-1 flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>
          <div>
            <label className="text-muted-foreground text-xs font-medium">期限 deadline_at</label>
            <Input
              type="datetime-local"
              value={deadlineAt}
              onChange={(e) => setDeadlineAt(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-muted-foreground text-xs font-medium">決策理由 decision_reason</label>
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
                  <label className="text-muted-foreground text-xs">承辦備註 note（選填）</label>
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
          <Button
            type="button"
            className="w-full"
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            送出補件
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
