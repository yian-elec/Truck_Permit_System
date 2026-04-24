function Metric({ label, value }: { label: string; value: string | number | undefined }) {
  return (
    <div className="rounded-xl border border-border bg-background p-5 shadow-sm">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="mt-2 text-3xl font-semibold tabular-nums text-foreground">{value ?? '—'}</p>
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
          <div key={i} className="h-24 animate-pulse rounded-xl bg-muted/40" />
        ))}
      </div>
    )
  }

  const extraPending = payloadMetrics?.pending_import_jobs
  const extraFailed = payloadMetrics?.failed_jobs_recent

  return (
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
  )
}
