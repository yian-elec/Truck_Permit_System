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
      title="啟用此圖資版本"
      description={`確定將「${layerLabel}」設為目前使用？啟用後，新的審查會以這份圖資為準；已立案案件不會自動重審。`}
      confirmLabel="確定啟用"
      loading={loading}
      onConfirm={onConfirm}
    />
  )
}
