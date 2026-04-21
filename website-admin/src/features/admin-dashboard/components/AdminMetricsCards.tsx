import { SectionCard } from '@/shared/ui'

function Metric({ label, value }: { label: string; value: string | number | undefined }) {
  return (
    <div className="border-border bg-card rounded-lg border p-4 shadow-sm">
      <p className="text-muted-foreground text-xs font-medium uppercase">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value ?? '—'}</p>
    </div>
  )
}

type Props = {
  loading?: boolean
  totalOpen?: number
  inReview?: number
  payloadMetrics?: Record<string, unknown>
}

export function AdminMetricsCards({ loading, totalOpen, inReview, payloadMetrics }: Props) {
  if (loading) {
    return (
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-muted/40 h-24 animate-pulse rounded-lg" />
        ))}
      </div>
    )
  }

  const extraPending = payloadMetrics?.pending_import_jobs
  const extraFailed = payloadMetrics?.failed_jobs_recent

  return (
    <SectionCard title="KPI 指標" description="待審與進行中任務取自審查 dashboard；其餘欄位若後端有填入 page model 一併顯示。">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="待審／開放任務" value={totalOpen} />
        <Metric label="審查中任務" value={inReview} />
        <Metric
          label="最近匯入作業"
          value={typeof extraPending === 'number' ? extraPending : '—'}
        />
        <Metric
          label="最近異常作業"
          value={typeof extraFailed === 'number' ? extraFailed : '—'}
        />
      </div>
    </SectionCard>
  )
}
