import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { workCenterUrl } from '@/shared/constants/route-paths'
import { ApiError } from '@/shared/api/api-error'
import { Button, DrawerPanel, JsonPreview, SectionCard, Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui'

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

const MAP_TABS = ['layers', 'kml', 'imports'] as const
type MapTab = (typeof MAP_TABS)[number]

function parseMapTab(raw: string | null): MapTab {
  if (raw && (MAP_TABS as readonly string[]).includes(raw)) return raw as MapTab
  return 'layers'
}

/** 匯入紀錄：優先顯示與 KML／圖資相關之作業；無法判斷時仍列出全部並加註說明。 */
function filterMapRelatedImportJobs(jobs: Record<string, unknown>[]) {
  const scored = jobs.filter((j) => {
    const jt = String(j.job_type ?? '').toLowerCase()
    const sn = String(j.source_name ?? j.source_description ?? '').toLowerCase()
    return jt.includes('kml') || jt.includes('map') || jt.includes('layer') || jt.includes('gis') || sn.includes('kml')
  })
  return scored.length > 0 ? scored : jobs
}

export function MapImportPage() {
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const tab = useMemo(() => parseMapTab(searchParams.get('tab')), [searchParams])

  const setTab = useCallback(
    (v: string) => {
      setSearchParams({ tab: v }, { replace: true })
    },
    [setSearchParams],
  )

  useEffect(() => {
    if (searchParams.get('tab') == null) {
      setSearchParams({ tab: 'layers' }, { replace: true })
    }
  }, [searchParams, setSearchParams])

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

  const mapImportJobs = useMemo(
    () => filterMapRelatedImportJobs((importsQuery.data ?? []) as Record<string, unknown>[]),
    [importsQuery.data],
  )

  const kmlMut = useMutation({
    mutationFn: requestKmlImport,
    onSuccess: async (data) => {
      toast.success(
        `匯入完成（作業 ${data.import_job_id}）。請至「目前使用中的圖資」分頁對新版本按「設為目前使用」，自動規劃才會套用此圖資。`,
      )
      await queryClient.invalidateQueries({ queryKey: queryKeys.ops.importJobs })
      await queryClient.refetchQueries({ queryKey: queryKeys.admin.mapLayers })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  const publishMut = useMutation({
    mutationFn: (layerId: string) => publishLayer(layerId),
    onSuccess: async (published: MapLayerItem) => {
      toast.success('已設為目前使用中的圖資')
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
    <div className="space-y-4">
      <SectionCard title="圖資與上傳">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="flex w-full flex-wrap gap-1">
            <TabsTrigger value="layers">目前使用中的圖資</TabsTrigger>
            <TabsTrigger value="kml">上傳新圖資（KML）</TabsTrigger>
            <TabsTrigger value="imports">上傳紀錄</TabsTrigger>
          </TabsList>

          <TabsContent value="layers" className="mt-4">
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
          </TabsContent>

          <TabsContent value="kml" className="mt-4">
            <KmlImportForm loading={kmlMut.isPending} onSubmit={(d) => kmlMut.mutate(d)} />
          </TabsContent>

          <TabsContent value="imports" className="mt-4">
            <p className="text-muted-foreground mb-3 text-sm">
              以下優先顯示與 KML／圖資相關之上傳紀錄。若需看<strong>全部</strong>圖資匯入，請至{' '}
              <Link className="text-primary underline underline-offset-2" to={workCenterUrl('import')}>
                待處理工作 → 圖資匯入
              </Link>
              。
            </p>
            <ImportJobTable jobs={mapImportJobs} onView={(id) => void openJob(id)} />
          </TabsContent>
        </Tabs>
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
