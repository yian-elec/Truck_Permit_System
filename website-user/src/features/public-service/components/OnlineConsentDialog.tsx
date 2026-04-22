import { useState } from 'react'

import { Button, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/shared/ui'
import {
  ONLINE_CONSENT_INTRO,
  ONLINE_CONSENT_POINT_5_SUB,
  ONLINE_CONSENT_POINTS,
  ONLINE_CONSENT_TITLE,
} from '@/shared/constants/online-consent-text'

type Mode = 'readOnly' | 'recordConsent'

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
  mode: Mode
  /**
   * 已寫入同意紀錄時只顯示全文與「關閉」，不再顯示勾選與「確認」。
   */
  consentAlreadyRecorded?: boolean
  /** recordConsent：按「確認」時呼叫；回傳 Promise 成功後關閉 */
  onConfirmRecord?: () => Promise<void>
  loading?: boolean
}

function ConsentClausesBody() {
  return (
    <div className="min-h-0 flex-1 overflow-y-auto px-6 py-4 text-sm leading-relaxed text-foreground">
      <p className="mb-4 font-medium">{ONLINE_CONSENT_INTRO}</p>
      <ol className="list-decimal space-y-3 pl-5">
        {ONLINE_CONSENT_POINTS.filter((p) => p.n <= 4).map((p) => (
          <li key={p.n}>{p.text}</li>
        ))}
        <li>
          {ONLINE_CONSENT_POINTS.find((x) => x.n === 5)?.text}
          <ul className="mt-2 list-none space-y-1 pl-0">
            {ONLINE_CONSENT_POINT_5_SUB.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </li>
        {ONLINE_CONSENT_POINTS.filter((p) => p.n >= 6).map((p) => (
          <li key={p.n}>{p.text}</li>
        ))}
      </ol>
    </div>
  )
}

export function OnlineConsentDialog({
  open,
  onOpenChange,
  mode,
  consentAlreadyRecorded = false,
  onConfirmRecord,
  loading = false,
}: Props) {
  const [innerChecked, setInnerChecked] = useState(false)

  const handleClose = () => {
    setInnerChecked(false)
    onOpenChange(false)
  }

  const viewOnly = consentAlreadyRecorded || mode === 'readOnly'

  const handleConfirm = async () => {
    if (!onConfirmRecord) return
    try {
      await onConfirmRecord()
      setInnerChecked(false)
      onOpenChange(false)
    } catch {
      /* 錯誤由呼叫端 toast；維持開啟以便重試 */
    }
  }

  const confirmDisabled = !innerChecked || loading

  const headerDescription = viewOnly
    ? mode === 'readOnly'
      ? '此處可先行閱讀全文。具法律效力之同意請至「預覽確認」頁，於線上申辦同意書視窗內勾選並按「確認」，寫入同意時間後，送件前檢查才會通過。'
      : '您已於系統完成申辦同意，以下全文僅供查閱。'
    : '請詳閱以下內容。'

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) setInnerChecked(false)
        onOpenChange(v)
      }}
    >
      <DialogContent className="flex max-h-[90vh] max-w-2xl flex-col gap-0 p-0">
        <DialogHeader className="shrink-0 border-b border-border px-6 pb-4 pt-6">
          <DialogTitle>{ONLINE_CONSENT_TITLE}</DialogTitle>
          <DialogDescription className="text-left text-sm text-muted-foreground">
            {headerDescription}
          </DialogDescription>
        </DialogHeader>

        <ConsentClausesBody />

        {viewOnly ? (
          <div className="shrink-0 border-t border-border bg-background px-6 py-4">
            <div className="flex justify-end">
              <Button type="button" onClick={handleClose}>
                關閉
              </Button>
            </div>
          </div>
        ) : (
          <div className="shrink-0 flex flex-col gap-3 border-t border-border bg-background px-6 py-4">
            <label className="flex cursor-pointer items-start gap-3 text-left text-sm">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border border-input"
                checked={innerChecked}
                onChange={(e) => setInnerChecked(e.target.checked)}
              />
              <span>我已閱讀並同意上述申辦同意書內容</span>
            </label>
            <div className="flex w-full flex-wrap justify-end gap-2">
              <Button type="button" variant="outline" onClick={handleClose}>
                取消
              </Button>
              <Button
                type="button"
                disabled={confirmDisabled}
                loading={loading}
                onClick={handleConfirm}
              >
                確認
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
