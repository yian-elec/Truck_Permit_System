import { useState } from 'react'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import { Button, SectionCard } from '@/shared/ui'

import { OnlineConsentDialog } from '@/features/public-service/components/OnlineConsentDialog'

import type { useAcceptConsent } from '../hooks/useAcceptConsent'

type Props = {
  consent: ReturnType<typeof useAcceptConsent>
  /** 已同意時，同意書視窗僅顯示「關閉」 */
  consentAcceptedAt: string | null | undefined
}

export function PreviewConsentPanel({ consent, consentAcceptedAt }: Props) {
  const [open, setOpen] = useState(false)
  const already = Boolean(consentAcceptedAt)

  return (
    <div id="section-preview-consent" className="scroll-mt-24">
      <SectionCard title="申辦同意書">
        <p className="text-sm text-muted-foreground">
          請點選下方按鈕開啟全文，在視窗內勾選並按「確認」即寫入同意紀錄，送件前檢查才會通過；無需另外勾選本區外之核取方塊。
        </p>
        <div className="mt-3">
          <Button type="button" variant="secondary" onClick={() => setOpen(true)}>
            點選線上申辦同意書
          </Button>

          <OnlineConsentDialog
            open={open}
            onOpenChange={setOpen}
            mode="recordConsent"
            consentAlreadyRecorded={already}
            loading={consent.isPending}
            onConfirmRecord={async () => {
              try {
                await consent.mutateAsync()
                toast.success('已記錄同意')
              } catch (e) {
                toast.error(getErrorMessage(e))
                throw e
              }
            }}
          />
        </div>
      </SectionCard>
    </div>
  )
}

export function canPreviewSubmit(consentAcceptedAt: string | null | undefined): boolean {
  return Boolean(consentAcceptedAt)
}
