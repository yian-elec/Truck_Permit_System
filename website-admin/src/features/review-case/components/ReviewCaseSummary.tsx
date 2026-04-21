import { formatDate } from '@/shared/utils/format-date'
import { InfoRow } from '@/shared/ui'

type App = Record<string, unknown>

export function ReviewCaseSummary({ application }: { application: App }) {
  const applicant = application.applicant as Record<string, unknown> | undefined
  const company = application.company as Record<string, unknown> | undefined
  const vehicles = (application.vehicles as Record<string, unknown>[] | undefined) ?? []

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <InfoRow label="申請期間（起）">
          {application.requested_start_at ? formatDate(String(application.requested_start_at)) : '—'}
        </InfoRow>
        <InfoRow label="申請期間（迄）">
          {application.requested_end_at ? formatDate(String(application.requested_end_at)) : '—'}
        </InfoRow>
        <InfoRow label="領件方式">{String(application.delivery_method ?? '')}</InfoRow>
        <InfoRow label="原因類型">{String(application.reason_type ?? '')}</InfoRow>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold">申請人</h3>
        {applicant ? (
          <div className="grid gap-2 sm:grid-cols-2">
            <InfoRow label="姓名">{String(applicant.name ?? '')}</InfoRow>
            <InfoRow label="Email">{String(applicant.email ?? '')}</InfoRow>
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">無申請人資料</p>
        )}
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold">公司</h3>
        {company ? (
          <div className="grid gap-2 sm:grid-cols-2">
            <InfoRow label="名稱">{String(company.company_name ?? '')}</InfoRow>
            <InfoRow label="統編">{String(company.tax_id ?? '')}</InfoRow>
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">無公司資料</p>
        )}
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold">車輛</h3>
        {vehicles.length === 0 ? (
          <p className="text-muted-foreground text-sm">無車輛</p>
        ) : (
          <ul className="divide-border divide-y rounded-md border text-sm">
            {vehicles.map((v, i) => (
              <li key={i} className="px-3 py-2 font-mono text-xs">
                {JSON.stringify(v)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
