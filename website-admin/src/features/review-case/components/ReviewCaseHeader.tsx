import { formatDate } from '@/shared/utils/format-date'
import { InfoRow } from '@/shared/ui'

type App = Record<string, unknown>

export function ReviewCaseHeader({ application }: { application: App }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <InfoRow label="案件 ID">{String(application.application_id ?? '')}</InfoRow>
      <InfoRow label="申請狀態">
        <span className="font-medium">{String(application.status ?? '')}</span>
      </InfoRow>
      <InfoRow label="申請編號">{String(application.application_no ?? '')}</InfoRow>
      <InfoRow label="最近更新">
        {application.updated_at ? formatDate(String(application.updated_at)) : '—'}
      </InfoRow>
    </div>
  )
}
