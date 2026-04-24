import { useQuery } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Navigate, useSearchParams } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { formatImportJobTypeForList, formatJobListStatus } from '@/shared/utils/admin-operator-copy'
import { formatDate } from '@/shared/utils/format-date'
import {
  DataTable,
  type DataTableColumn,
  DrawerPanel,
  JsonPreview,
  SectionCard,
  StatusBadge,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'

import {
  getOcrJob,
  getOpsImportJob,
  listImportJobs,
  listNotificationJobs,
  listOcrJobs,
} from '@/features/admin-ops/api/ops-api'
import { listReviewTasks } from '@/features/review-task/api/review-task-api'
import { ReviewTaskListContent } from '@/features/review-task/components/ReviewTaskListContent'

const TAB_VALUES = ['review', 'ocr', 'notif', 'import'] as const
type WorkTab = (typeof TAB_VALUES)[number]

type Row = Record<string, unknown>

function parseTab(raw: string | null): WorkTab {
  if (raw && (TAB_VALUES as readonly string[]).includes(raw)) return raw as WorkTab
  return 'review'
}

export function WorkCenterPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const tab = useMemo(() => parseTab(searchParams.get('tab')), [searchParams])

  const setTab = useCallback(
    (v: string) => {
      setSearchParams({ tab: v }, { replace: true })
    },
    [setSearchParams],
  )

  useEffect(() => {
    if (searchParams.get('tab') == null) {
      setSearchParams({ tab: 'review' }, { replace: true })
    }
  }, [searchParams, setSearchParams])

  const [detail, setDetail] = useState<{ title: string; payload: unknown } | null>(null)

  const ocrQ = useQuery({ queryKey: queryKeys.ops.ocrJobs, queryFn: listOcrJobs })
  const nq = useQuery({ queryKey: queryKeys.ops.notificationJobs, queryFn: listNotificationJobs })
  const iq = useQuery({ queryKey: queryKeys.ops.importJobs, queryFn: listImportJobs })
  const reviewListQ = useQuery({
    queryKey: [...queryKeys.review.tasks, 50, 0] as const,
    queryFn: () => listReviewTasks({ limit: 50, offset: 0 }),
  })

  const tabCount = (n: number | undefined) => (typeof n === 'number' ? n : 0)
  const cReview = tabCount(reviewListQ.data?.length)
  const cOcr = tabCount(ocrQ.data?.length)
  const cN = tabCount(nq.data?.length)
  const cI = tabCount(iq.data?.length)

  if (searchParams.get('tab') === 'audit') {
    return <Navigate to={routePaths.auditLog} replace />
  }

  const ocrCols: DataTableColumn<Row>[] = [
    { id: 'id', header: '辨識編號', cell: (r) => <span className="font-mono text-xs">{String(r.ocr_job_id ?? r.id ?? '')}</span> },
    {
      id: 'st',
      header: '狀態',
      cell: (r) => <StatusBadge status={formatJobListStatus(String(r.status ?? ''))} />,
    },
    { id: 's', header: '開始時間', cell: (r) => (r.started_at ? formatDate(String(r.started_at)) : '—') },
    { id: 'f', header: '完成時間', cell: (r) => (r.finished_at ? formatDate(String(r.finished_at)) : '—') },
    {
      id: 'a',
      header: '',
      cell: (r) => {
        const id = String(r.ocr_job_id ?? r.id ?? '')
        return (
          <button
            type="button"
            className="text-primary text-sm underline"
            onClick={async () => {
              if (!id) return
              const data = await getOcrJob(id)
              setDetail({ title: `文件辨識 ${id}`, payload: data })
            }}
          >
            詳情
          </button>
        )
      },
    },
  ]

  const njCols: DataTableColumn<Row>[] = [
    { id: 'id', header: '紀錄編號', cell: (r) => <span className="font-mono text-xs">{String(r.notification_job_id ?? '')}</span> },
    { id: 'ch', header: '發送管道', cell: (r) => String(r.channel ?? '') },
    { id: 'to', header: '收件人', cell: (r) => String(r.recipient ?? r.to_recipient ?? '') },
    {
      id: 'st',
      header: '狀態',
      cell: (r) => <StatusBadge status={formatJobListStatus(String(r.status ?? ''))} />,
    },
  ]

  const ijCols: DataTableColumn<Row>[] = [
    { id: 'id', header: '匯入編號', cell: (r) => <span className="font-mono text-xs">{String(r.import_job_id ?? '')}</span> },
    {
      id: 'jt',
      header: '作業類型',
      cell: (r) => {
        const raw = String(r.job_type ?? '')
        const label = formatImportJobTypeForList(raw)
        return (
          <span className="text-sm" title={raw || undefined}>
            {label}
          </span>
        )
      },
    },
    { id: 'sn', header: '來源名稱', cell: (r) => String(r.source_name ?? r.source_description ?? '') },
    {
      id: 'st',
      header: '狀態',
      cell: (r) => <StatusBadge status={formatJobListStatus(String(r.status ?? ''))} />,
    },
    {
      id: 'a',
      header: '',
      cell: (r) => {
        const id = String(r.import_job_id ?? '')
        return (
          <button
            type="button"
            className="text-primary text-sm underline"
            onClick={async () => {
              if (!id) return
              const data = await getOpsImportJob(id)
              setDetail({ title: `圖資匯入作業 ${id}`, payload: data })
            }}
          >
            詳情
          </button>
        )
      },
    },
  ]

  return (
    <div className="space-y-4">
      <SectionCard title="待處理工作">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="flex w-full flex-wrap gap-1">
            <TabsTrigger value="review">申請審核 {cReview}</TabsTrigger>
            <TabsTrigger value="ocr">文件辨識 {cOcr}</TabsTrigger>
            <TabsTrigger value="notif">通知紀錄 {cN}</TabsTrigger>
            <TabsTrigger value="import">圖資匯入 {cI}</TabsTrigger>
          </TabsList>
          <TabsContent value="review" className="mt-4">
            <ReviewTaskListContent embedded />
          </TabsContent>
          <TabsContent value="ocr" className="mt-4">
            {ocrQ.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : (
              <DataTable columns={ocrCols} data={ocrQ.data ?? []} getRowId={(r) => String(r.ocr_job_id ?? r.id ?? '')} />
            )}
          </TabsContent>
          <TabsContent value="notif" className="mt-4">
            {nq.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : (
              <DataTable columns={njCols} data={nq.data ?? []} getRowId={(r) => String(r.notification_job_id ?? '')} />
            )}
          </TabsContent>
          <TabsContent value="import" className="mt-4">
            {iq.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : (
              <DataTable columns={ijCols} data={iq.data ?? []} getRowId={(r) => String(r.import_job_id ?? '')} />
            )}
          </TabsContent>
        </Tabs>
      </SectionCard>

      <DrawerPanel open={detail != null} onOpenChange={(o) => !o && setDetail(null)} title={detail?.title ?? ''}>
        {detail ? <JsonPreview value={detail.payload} /> : null}
      </DrawerPanel>
    </div>
  )
}
