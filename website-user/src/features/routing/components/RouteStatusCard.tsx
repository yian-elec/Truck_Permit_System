import { SectionCard } from '@/shared/ui'

export function RouteStatusCard({ status }: { status?: string }) {
  return (
    <SectionCard title="Route status">
      <p className="text-sm">{status ?? 'Unknown'}</p>
    </SectionCard>
  )
}
