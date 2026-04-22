import { SectionCard } from '@/shared/ui'

import { missingReasonToMessage } from '../lib/missing-reason-messages'
import type { SubmissionCheckResult } from '../api/get-submission-check'

export function SubmissionCheckPanel({ data }: { data: SubmissionCheckResult | null | undefined }) {
  if (!data) {
    return (
      <SectionCard title="送件檢查">
        <p className="text-sm text-muted-foreground">尚無資料。</p>
      </SectionCard>
    )
  }

  return (
    <SectionCard title="送件檢查">
      <p className="text-sm">
        <span className="font-medium">可否送件：</span>{' '}
        {data.can_submit ? '是' : '否'}
      </p>
      {data.missing_reason_codes?.length ? (
        <div className="mt-3">
          <p className="text-sm font-medium text-destructive">缺少項目</p>
          <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
            {data.missing_reason_codes.map((code) => (
              <li key={code}>{missingReasonToMessage(code)}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="mt-2 text-sm text-muted-foreground">未回報阻擋送件原因。</p>
      )}
    </SectionCard>
  )
}
