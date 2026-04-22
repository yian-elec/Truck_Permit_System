import { useState } from 'react'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import { Button, SectionCard } from '@/shared/ui'
import { formatDate } from '@/shared/utils/format-date'

import { useConsentLatest } from '@/features/public-service/hooks/useConsentLatest'
import { OnlineConsentDialog } from '@/features/public-service/components/OnlineConsentDialog'

import { useApplicationDetail } from '../hooks/useApplicationDetail'
import { useAcceptConsent } from '../hooks/useAcceptConsent'

const SUMMARY =
  '使用本服務即表示您已閱讀並理解個人資料蒐集、利用與送件責任等事項。請於下方開啟線上申辦同意書、勾選並按「確認」，或至「預覽確認」頁完成相同步驟，系統才會寫入同意時間供送件檢查。'

type Props = {
  applicationId: string
  className?: string
}

/**
 * 申請編輯頁之申辦同意書：開啟與預覽頁相同之視窗，按確認時呼叫 POST …/consent 寫入同意紀錄。
 */
export function ApplicationConsentSummarySection({ applicationId, className }: Props) {
  const [open, setOpen] = useState(false)
  const latest = useConsentLatest()
  const detail = useApplicationDetail(applicationId)
  const accept = useAcceptConsent(applicationId)
  const meta = latest.isSuccess && latest.data
    ? `同意書版本 ${latest.data.version} · 生效日 ${latest.data.effective_at}`
    : null
  const acceptedAt = detail.data?.consent_accepted_at

  return (
    <div id="section-consent" className={`scroll-mt-24 ${className ?? ''}`}>
      <SectionCard
        title="申辦同意書"
        description="可於本區或「預覽確認」頁開啟同意書；於視窗內勾選並按「確認」即寫入同意紀錄。以下為靜態摘要，版本資訊如下。"
      >
        {meta ? <p className="text-xs text-muted-foreground">{meta}</p> : null}
        {acceptedAt ? (
          <p className="mt-2 text-sm text-emerald-700">
            已於 {formatDate(acceptedAt, 'zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' })}{' '}
            完成申辦同意書
          </p>
        ) : null}
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          {acceptedAt
            ? '您已完成申辦同意，仍可隨時點下方按鈕查閱完整內文。'
            : SUMMARY}
        </p>
        <Button
          className="mt-4"
          variant="outline"
          size="sm"
          type="button"
          onClick={() => setOpen(true)}
        >
          點選線上申辦同意書
        </Button>
        <OnlineConsentDialog
          open={open}
          onOpenChange={setOpen}
          mode="recordConsent"
          consentAlreadyRecorded={Boolean(acceptedAt)}
          loading={accept.isPending}
          onConfirmRecord={async () => {
            try {
              await accept.mutateAsync()
              toast.success('已記錄同意')
            } catch (e) {
              toast.error(getErrorMessage(e))
              throw e
            }
          }}
        />
      </SectionCard>
    </div>
  )
}
