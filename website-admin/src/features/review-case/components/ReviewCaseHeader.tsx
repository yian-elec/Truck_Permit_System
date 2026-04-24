import { formatDate } from '@/shared/utils/format-date'
import { formatOperatorStage, formatOperatorStatus } from '@/shared/utils/admin-operator-copy'
import { InfoRow, StatusBadge } from '@/shared/ui'

type App = Record<string, unknown>

export function ReviewCaseHeader({ application }: { application: App }) {
  const applicant = application.applicant as Record<string, unknown> | undefined
  const company = application.company as Record<string, unknown> | undefined
  const vehicles = (application.vehicles as Record<string, unknown>[] | undefined) ?? []
  const v0 = vehicles[0]
  const plate = v0 != null ? String(v0.plate_no ?? v0.vehicle_id ?? '—') : '—'
  const name = applicant?.name
    ? String(applicant.name)
    : company?.company_name
      ? String(company.company_name)
      : '—'

  return (
    <div className="space-y-3">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <InfoRow label="申請編號">
          <span className="font-medium text-foreground">{String(application.application_no ?? '—')}</span>
        </InfoRow>
        <InfoRow label="申請人 / 單位">{name}</InfoRow>
        <InfoRow label="車牌">{plate}</InfoRow>
        <InfoRow label="申請期間（起）">
          {application.requested_start_at ? formatDate(String(application.requested_start_at)) : '—'}
        </InfoRow>
        <InfoRow label="申請期間（迄）">
          {application.requested_end_at ? formatDate(String(application.requested_end_at)) : '—'}
        </InfoRow>
        <InfoRow label="辦理階段">
          {formatOperatorStage(String(application.stage ?? application.review_stage ?? ''))}
        </InfoRow>
        <InfoRow label="目前狀態">
          <StatusBadge status={formatOperatorStatus(String(application.status ?? ''))} />
        </InfoRow>
        <InfoRow label="最後更新">
          {application.updated_at ? formatDate(String(application.updated_at)) : '—'}
        </InfoRow>
      </div>
    </div>
  )
}
