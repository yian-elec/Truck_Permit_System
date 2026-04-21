import { SectionCard } from '@/shared/ui'

export function PermitSummaryCard({ data }: { data: unknown }) {
  const d = data as {
    permit_no?: string
    status?: string
    approved_start_at?: string
    approved_end_at?: string
    route_summary_text?: string
    certificate?: {
      status?: string
      version_no?: number
      downloadable?: boolean
      generated_at?: string | null
    } | null
  }

  return (
    <SectionCard title="通行證">
      <dl className="grid gap-2 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-muted-foreground">證號</dt>
          <dd className="font-medium">{d.permit_no ?? '—'}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">狀態</dt>
          <dd className="font-medium">{d.status ?? '—'}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">生效起</dt>
          <dd>{d.approved_start_at ?? '—'}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">生效迄</dt>
          <dd>{d.approved_end_at ?? '—'}</dd>
        </div>
      </dl>
      {d.certificate ? (
        <div className="mt-4 rounded-md border border-border bg-muted/30 px-3 py-2 text-sm">
          <p className="font-medium text-foreground">使用證檔案</p>
          <dl className="mt-2 grid gap-1 sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">憑證狀態</dt>
              <dd>{d.certificate.status ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">可下載</dt>
              <dd>{d.certificate.downloadable ? '是' : '否'}</dd>
            </div>
            {d.certificate.version_no != null ? (
              <div>
                <dt className="text-muted-foreground">版本</dt>
                <dd>{d.certificate.version_no}</dd>
              </div>
            ) : null}
          </dl>
        </div>
      ) : null}
      {d.route_summary_text ? (
        <p className="mt-4 text-sm text-muted-foreground">{d.route_summary_text}</p>
      ) : null}
    </SectionCard>
  )
}
