import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { Button, DrawerPanel, JsonPreview, SectionCard } from '@/shared/ui'

import {
  listMapLayers,
  publishLayer,
  type MapLayerItem,
} from '@/features/admin-map-layer/api/map-layer-api'
import { MapLayerTable } from '@/features/admin-map-layer/components/MapLayerTable'
import { PublishLayerDialog } from '@/features/admin-map-layer/components/PublishLayerDialog'

import { getImportJob, requestKmlImport } from '../api/map-import-api'
import { ImportJobTable } from '../components/ImportJobTable'
import { KmlImportForm } from '../components/KmlImportForm'
import { listImportJobs } from '@/features/admin-ops/api/ops-api'

export function MapImportPage() {
  const queryClient = useQueryClient()
  const [jobDetail, setJobDetail] = useState<Record<string, unknown> | null>(null)
  const [publishTarget, setPublishTarget] = useState<{ id: string; label: string } | null>(null)

  const layersQuery = useQuery({
    queryKey: queryKeys.admin.mapLayers,
    queryFn: listMapLayers,
  })

  const importsQuery = useQuery({
    queryKey: queryKeys.ops.importJobs,
    queryFn: listImportJobs,
  })

  const kmlMut = useMutation({
    mutationFn: requestKmlImport,
    onSuccess: async (data) => {
      toast.success(
        `匯入完成（作業 ${data.import_job_id}）。請至下方「圖資 Layer」對新版本按「發布」，自動規劃才會套用此圖資。`,
      )
      await queryClient.invalidateQueries({ queryKey: queryKeys.ops.importJobs })
      await queryClient.refetchQueries({ queryKey: queryKeys.admin.mapLayers })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  const publishMut = useMutation({
    mutationFn: (layerId: string) => publishLayer(layerId),
    onSuccess: async (published: MapLayerItem) => {
      toast.success('已發布')
      setPublishTarget(null)
      queryClient.setQueryData<MapLayerItem[]>(queryKeys.admin.mapLayers, (old) => {
        if (!old?.length) return old
        return old.map((row) =>
          row.layer_id === published.layer_id ? { ...row, ...published } : row,
        )
      })
      await queryClient.invalidateQueries({ queryKey: queryKeys.admin.mapLayers })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  async function openJob(id: string) {
    try {
      const j = await getImportJob(id)
      setJobDetail(j)
    } catch (e) {
      toast.error(ApiError.fromUnknown(e).message)
    }
  }

  return (
    <div className="space-y-6">
      <SectionCard title="KML 匯入">
        <KmlImportForm loading={kmlMut.isPending} onSubmit={(d) => kmlMut.mutate(d)} />
      </SectionCard>

      <SectionCard title="匯入作業（Ops import jobs）">
        <ImportJobTable jobs={importsQuery.data ?? []} onView={(id) => void openJob(id)} />
      </SectionCard>

      <SectionCard title="圖資 Layer">
        {layersQuery.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : layersQuery.isError ? (
          <div className="space-y-2">
            <p className="text-destructive text-sm">
              無法載入圖資列表（{ApiError.fromUnknown(layersQuery.error).message}）。若曾設定 API
              位址，請確認 <code className="text-xs">VITE_API_BASE_URL</code> 指向與匯入相同的後端。
            </p>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => void layersQuery.refetch()}
            >
              重試
            </Button>
          </div>
        ) : (
          <MapLayerTable
            layers={layersQuery.data ?? []}
            publishingId={publishMut.isPending ? publishTarget?.id : null}
            onPublish={(layerId) => {
              const layer = layersQuery.data?.find((l) => l.layer_id === layerId)
              setPublishTarget({ id: layerId, label: layer?.layer_name ?? layerId })
            }}
          />
        )}
      </SectionCard>

      <DrawerPanel
        open={jobDetail != null}
        onOpenChange={(o) => !o && setJobDetail(null)}
        title="匯入作業詳情"
      >
        {jobDetail ? <JsonPreview value={jobDetail} /> : null}
      </DrawerPanel>

      <PublishLayerDialog
        open={publishTarget != null}
        onOpenChange={(o) => !o && setPublishTarget(null)}
        layerLabel={publishTarget?.label ?? ''}
        loading={publishMut.isPending}
        onConfirm={() => publishTarget && publishMut.mutate(publishTarget.id)}
      />
    </div>
  )
}
