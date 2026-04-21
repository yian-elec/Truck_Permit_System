import { ConfirmDialog } from '@/shared/ui'

export function PublishLayerDialog({
  open,
  onOpenChange,
  layerLabel,
  onConfirm,
  loading,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  layerLabel: string
  onConfirm: () => void
  loading?: boolean
}) {
  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      title="發布圖資版本"
      description={`確定發布 ${layerLabel}？`}
      confirmLabel="發布"
      loading={loading}
      onConfirm={onConfirm}
    />
  )
}
