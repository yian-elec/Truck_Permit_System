import { Button } from '@/shared/ui'

export type VehicleCardProps = {
  plateNo: string
  kind?: string
  weight?: string | number
  onEdit?: () => void
  onDelete?: () => void
}

export function VehicleCard({ plateNo, kind, weight, onEdit, onDelete }: VehicleCardProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border p-3 text-sm">
      <div>
        <p className="font-medium">{plateNo}</p>
        <p className="text-xs text-muted-foreground">
          {kind ?? '—'} · {weight ?? '—'} 噸
        </p>
      </div>
      <div className="flex gap-2">
        {onEdit ? (
          <Button variant="outline" size="sm" type="button" onClick={onEdit}>
            編輯
          </Button>
        ) : null}
        {onDelete ? (
          <Button variant="destructive" size="sm" type="button" onClick={onDelete}>
            刪除
          </Button>
        ) : null}
      </div>
    </div>
  )
}
