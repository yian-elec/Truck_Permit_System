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
    { id: 'code', header: '系統代碼', cell: (r) => <span className="font-mono text-xs text-muted-foreground">{r.layer_code}</span> },
    { id: 'name', header: '圖資名稱', cell: (r) => r.layer_name },
    { id: 'ver', header: '版本', cell: (r) => r.version_no },
    {
      id: 'active',
      header: '使用狀態',
      cell: (r) => (
        <StatusBadge status={r.is_active ? '已啟用' : '未啟用'} />
      ),
    },
    {
      id: 'published',
      header: '啟用時間',
      cell: (r) => (
        <span className="text-muted-foreground tabular-nums">
          {r.published_at ? new Date(r.published_at).toLocaleString() : '—'}
        </span>
      ),
    },
    {
      id: 'pub',
      header: '操作',
      cell: (r) => (
        <button
          type="button"
          className="text-primary text-sm font-medium underline disabled:opacity-50"
          disabled={publishingId === r.layer_id}
          onClick={() => onPublish(r.layer_id)}
        >
          {publishingId === r.layer_id ? '處理中…' : '設為目前使用'}
        </button>
      ),
    },
  ]

  return <DataTable columns={columns} data={layers} getRowId={(r) => r.layer_id} />
}
