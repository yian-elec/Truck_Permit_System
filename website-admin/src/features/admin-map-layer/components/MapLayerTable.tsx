import { DataTable, type DataTableColumn, StatusBadge } from '@/shared/ui'

import type { MapLayerItem } from '../api/map-layer-api'

export function MapLayerTable({
  layers,
  onPublish,
  publishingId,
}: {
  layers: MapLayerItem[]
  onPublish: (layerId: string) => void
  publishingId?: string | null
}) {
  const columns: DataTableColumn<MapLayerItem>[] = [
    { id: 'code', header: 'layer_code', cell: (r) => r.layer_code },
    { id: 'name', header: 'layer_name', cell: (r) => r.layer_name },
    { id: 'ver', header: 'version_no', cell: (r) => r.version_no },
    {
      id: 'active',
      header: '啟用狀態',
      cell: (r) => (
        <StatusBadge status={r.is_active ? '已啟用' : '未啟用'} />
      ),
    },
    {
      id: 'published',
      header: 'published_at',
      cell: (r) => (
        <span className="text-muted-foreground tabular-nums">
          {r.published_at ? new Date(r.published_at).toLocaleString() : '—'}
        </span>
      ),
    },
    {
      id: 'pub',
      header: '',
      cell: (r) => (
        <button
          type="button"
          className="text-primary text-sm font-medium underline disabled:opacity-50"
          disabled={publishingId === r.layer_id}
          onClick={() => onPublish(r.layer_id)}
        >
          {publishingId === r.layer_id ? '發布中…' : '發布圖資'}
        </button>
      ),
    },
  ]

  return <DataTable columns={columns} data={layers} getRowId={(r) => r.layer_id} />
}
