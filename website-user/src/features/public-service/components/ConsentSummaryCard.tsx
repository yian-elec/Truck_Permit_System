import { Link } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { Button } from '@/shared/ui'

import type { ConsentLatest } from '../types/public-service.types'

export function ConsentSummaryCard({ data }: { data: ConsentLatest }) {
  return (
    <section className="rounded-lg border border-border bg-background p-6 shadow-sm">
      <h3 className="text-lg font-semibold">同意條款摘要</h3>
      <p className="mt-2 text-xs text-muted-foreground">
        版本 {data.version} · 生效日 {data.effective_at}
      </p>
      <p className="mt-4 text-sm leading-relaxed text-muted-foreground">{data.summary}</p>
      <p className="mt-3 text-xs text-muted-foreground">
        送件前須同意：{data.must_accept_before_submit ? '是' : '否'}
      </p>
      <Button className="mt-4" variant="outline" size="sm" asChild>
        <Link to={routePaths.consent}>查看完整條款</Link>
      </Button>
    </section>
  )
}
