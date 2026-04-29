import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { ApiError } from '@/shared/api/api-error'
import { Button, InfoRow, SectionCard } from '@/shared/ui'

import {
  getRoutePlan,
  getRouteRequestPreview,
  getRuleHits,
  replanRoute,
  selectCandidate,
} from '../api/route-api'
import { CandidateList } from '../components/CandidateList'
import { SelectedRouteEditDialog } from '../components/SelectedRouteEditDialog'
import { RoutePlanPanel } from '../components/RoutePlanPanel'
import { RuleHitsPanel } from '../components/RuleHitsPanel'
import { SelectedRouteItinerary } from '../components/SelectedRouteItinerary'
import { readOptStr } from '../utils/route-plan-fields'

/** 後端 UC-ROUTE-02 失敗時多為 404 + RoutingNotFoundAppError（LookupError 映射）。 */
function formatReplanFailureMessage(error: unknown): string {
  const err = ApiError.fromUnknown(error)
  const m = err.message ?? ''
  if (err.status === 404 && err.code === 'RoutingNotFoundAppError') {
    if (m.includes('no_route_request') || m.includes('no route_request')) {
      return '找不到路線申請紀錄（routing 無資料），無法自動規劃。請確認申請人已於申請端儲存路線需求。'
    }
    if (m.includes('not ready for planning')) {
      return '路線申請目前狀態無法自動規劃（例如地理編碼失敗）。請申請人修正地址後重新儲存路線，或洽系統管理員。'
    }
    if (m.includes('missing geocoded points')) {
      return '路線申請缺少起迄座標，無法規劃。請確認地址可被地理編碼後再試。'
    }
  }
  return err.message
}

export function ReviewRoutePage() {
  const { applicationId = '' } = useParams<{ applicationId: string }>()
  const queryClient = useQueryClient()
  const [editRouteOpen, setEditRouteOpen] = useState(false)

  const planQuery = useQuery({
    queryKey: queryKeys.review.routePlan(applicationId),
    queryFn: () => getRoutePlan(applicationId),
    enabled: Boolean(applicationId),
  })

  const previewQuery = useQuery({
    queryKey: queryKeys.review.routePreview(applicationId),
    queryFn: () => getRouteRequestPreview(applicationId),
    enabled: Boolean(applicationId),
  })

  const hitsQuery = useQuery({
    queryKey: queryKeys.review.ruleHits(applicationId),
    queryFn: () => getRuleHits(applicationId),
    enabled: Boolean(applicationId),
  })

  const selectMut = useMutation({
    mutationFn: (candidateId: string) => selectCandidate(applicationId, candidateId),
    onSuccess: async () => {
      toast.success('已選定路線')
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.routePlan(applicationId) })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  const replanMut = useMutation({
    mutationFn: () => replanRoute(applicationId),
    onSuccess: async () => {
      toast.success('已執行自動規劃')
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.routePlan(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.routePreview(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.ruleHits(applicationId) })
    },
    onError: (e) => toast.error(formatReplanFailureMessage(e)),
  })

  const plan = planQuery.data as Record<string, unknown> | null | undefined
  const candidates = (plan?.candidates ?? []) as Record<string, unknown>[]

  if (planQuery.isLoading) return <p className="text-muted-foreground text-sm">載入路線…</p>
  if (planQuery.isError) {
    return <p className="text-destructive text-sm">無法載入路線規劃</p>
  }

  if (!plan) {
    const pv = previewQuery.data
    const originLabel = pv ? readOptStr(pv, 'origin_text') : undefined
    const destLabel = pv ? readOptStr(pv, 'destination_text') : undefined

    return (
      <div className="space-y-6 pb-16">
        <SectionCard title="路線規劃">
          <div className="space-y-3">
            {previewQuery.isLoading ? (
              <p className="text-muted-foreground text-sm">讀取申請路線起迄…</p>
            ) : pv ? (
              <div className="border-border rounded-md border bg-muted/20 px-3 py-2">
                <p className="text-muted-foreground mb-2 text-xs font-medium">申請路線起迄</p>
                <div className="grid gap-2 sm:grid-cols-2">
                  <InfoRow label="起始點">{originLabel ?? '—'}</InfoRow>
                  <InfoRow label="到達點">{destLabel ?? '—'}</InfoRow>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground text-xs">
                尚無路線申請紀錄（申請人可能尚未於申請端儲存起迄點）。
              </p>
            )}
            <p className="text-muted-foreground text-sm">
              尚無自動規劃結果。請確認申請人已儲存路線後，點選「執行自動規劃」以產生候選路線。
            </p>
          </div>
        </SectionCard>
        <SectionCard title="規則命中">
          <p className="text-muted-foreground text-sm">尚無路線規劃時無規則命中資料。</p>
        </SectionCard>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" loading={replanMut.isPending} onClick={() => replanMut.mutate()}>
            執行自動規劃
          </Button>
          <Button asChild variant="default">
            <Link to={routePaths.reviewCase(applicationId)}>返回案件審核</Link>
          </Button>
        </div>
      </div>
    )
  }

  const selectedId =
    (plan.selected_candidate_id as string | null | undefined) ??
    (plan['selected_candidate_id'] as string | null | undefined)

  const noRouteRaw = plan.no_route ?? plan['no_route']
  const noRouteMessage =
    noRouteRaw != null &&
    typeof noRouteRaw === 'object' &&
    noRouteRaw !== null &&
    'message' in noRouteRaw
      ? String((noRouteRaw as { message?: string }).message ?? '')
      : ''

  return (
    <div className="space-y-6 pb-16">
      <SectionCard title="路線摘要">
        <RoutePlanPanel
          status={String(plan.status ?? plan['status'] ?? '')}
          mapVersion={String(plan.map_version ?? plan['map_version'] ?? '')}
          planningVersion={String(plan.planning_version ?? plan['planning_version'] ?? '')}
          selectedCandidateId={selectedId ?? undefined}
          originText={readOptStr(plan, 'origin_text')}
          destinationText={readOptStr(plan, 'destination_text')}
        />
      </SectionCard>

      {noRouteMessage ? (
        <SectionCard title="無可行路線">
          <p className="text-destructive text-sm whitespace-pre-wrap">{noRouteMessage}</p>
        </SectionCard>
      ) : null}

      <SectionCard title="候選路線">
        <CandidateList
          candidates={candidates}
          selectedId={selectedId ?? undefined}
          onSelect={(id) => selectMut.mutate(id)}
        />
      </SectionCard>

      <SectionCard
        title="已選路線 — 行經道路"

      >
        <SelectedRouteItinerary candidates={candidates} selectedId={selectedId ?? undefined} />
      </SectionCard>

      <SectionCard title="規則命中">
        {hitsQuery.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : hitsQuery.isError ? (
          <p className="text-destructive text-sm">無法載入規則命中</p>
        ) : hitsQuery.data ? (
          <RuleHitsPanel hits={(hitsQuery.data.hits ?? []) as Record<string, unknown>[]} />
        ) : (
          <p className="text-muted-foreground text-sm">尚無規則命中資料（可能與目前路線版本相同）。</p>
        )}
      </SectionCard>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant="outline"
          disabled={!selectedId}
          onClick={() => setEditRouteOpen(true)}
        >
          調整已選路線
        </Button>
        <Button type="button" variant="secondary" loading={replanMut.isPending} onClick={() => replanMut.mutate()}>
          執行自動規劃
        </Button>
        <Button asChild variant="default">
          <Link to={routePaths.reviewCase(applicationId)}>返回案件審核</Link>
        </Button>
      </div>

      <SelectedRouteEditDialog
        applicationId={applicationId}
        open={editRouteOpen}
        onOpenChange={setEditRouteOpen}
        candidates={candidates}
        selectedId={selectedId ?? undefined}
      />
    </div>
  )
}
