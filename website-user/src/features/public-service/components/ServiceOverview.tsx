import type { ServiceOverview as ServiceOverviewModel } from '../types/public-service.types'

export function ServiceOverview({ data }: { data: ServiceOverviewModel }) {
  return (
    <section className="rounded-lg border border-border bg-background p-6 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{data.service_code}</p>
      <h2 className="mt-2 text-2xl font-semibold tracking-tight">{data.display_name}</h2>
      <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{data.description}</p>
      <p className="mt-4 text-xs text-muted-foreground">API 版本 {data.api_version}</p>
    </section>
  )
}
