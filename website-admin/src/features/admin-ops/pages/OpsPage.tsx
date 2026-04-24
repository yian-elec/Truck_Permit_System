import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { queryKeys } from '@/shared/constants/query-keys'
import { formatDate } from '@/shared/utils/format-date'
import { DataTable, type DataTableColumn, DrawerPanel, JsonPreview, SectionCard, Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui'

import {
  getOcrJob,
  getOpsImportJob,
  listAuditLogs,
  listImportJobs,
  listNotificationJobs,
  listOcrJobs,
} from '../api/ops-api'

type Row = Record<string, unknown>

export function OpsPage() {
  const [detail, setDetail] = useState<{ title: string; payload: unknown } | null>(null)

  const ocrQ = useQuery({ queryKey: queryKeys.ops.ocrJobs, queryFn: listOcrJobs })
  const nq = useQuery({ queryKey: queryKeys.ops.notificationJobs, queryFn: listNotificationJobs })
  const iq = useQuery({ queryKey: queryKeys.ops.importJobs, queryFn: listImportJobs })
  const aq = useQuery({ queryKey: queryKeys.ops.auditLogs, queryFn: listAuditLogs })

  const ocrCols: DataTableColumn<Row>[] = [
    { id: 'id', header: 'OCR 任務編號', cell: (r) => <span className="font-mono text-xs">{String(r.ocr_job_id ?? r.id ?? '')}</span> },
    { id: 'st', header: '狀態', cell: (r) => String(r.status ?? '') },
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
              setDetail({ title: `OCR ${id}`, payload: data })
            }}
          >
            詳情
          </button>
        )
      },
    },
  ]

  const njCols: DataTableColumn<Row>[] = [
    { id: 'id', header: '通知任務編號', cell: (r) => <span className="font-mono text-xs">{String(r.notification_job_id ?? '')}</span> },
    { id: 'ch', header: '發送管道', cell: (r) => String(r.channel ?? '') },
    { id: 'to', header: '收件人', cell: (r) => String(r.recipient ?? r.to_recipient ?? '') },
    { id: 'st', header: '狀態', cell: (r) => String(r.status ?? '') },
  ]

  const ijCols: DataTableColumn<Row>[] = [
    { id: 'id', header: '匯入任務編號', cell: (r) => <span className="font-mono text-xs">{String(r.import_job_id ?? '')}</span> },
    { id: 'jt', header: '作業類型', cell: (r) => String(r.job_type ?? '') },
    { id: 'sn', header: '來源名稱', cell: (r) => String(r.source_name ?? r.source_description ?? '') },
    { id: 'st', header: '狀態', cell: (r) => String(r.status ?? '') },
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
              setDetail({ title: `Import ${id}`, payload: data })
            }}
          >
            詳情
          </button>
        )
      },
    },
  ]

  const auditCols: DataTableColumn<Row>[] = [
    { id: 'id', header: '稽核編號', cell: (r) => <span className="font-mono text-xs">{String(r.audit_log_id ?? r.id ?? '')}</span> },
    { id: 'at', header: '操作者類型', cell: (r) => String(r.actor_type ?? '') },
    { id: 'ac', header: '操作代碼', cell: (r) => String(r.action_code ?? '') },
    { id: 'rt', header: '資源類型', cell: (r) => String(r.resource_type ?? '') },
    { id: 'ca', header: '發生時間', cell: (r) => (r.created_at ? formatDate(String(r.created_at)) : '—') },
  ]

  return (
    <div className="space-y-4">
      <SectionCard title="Ops 查詢" >
        <Tabs defaultValue="ocr">
          <TabsList>
            <TabsTrigger value="ocr">OCR 任務</TabsTrigger>
            <TabsTrigger value="notif">通知任務</TabsTrigger>
            <TabsTrigger value="import">匯入任務</TabsTrigger>
            <TabsTrigger value="audit">稽核紀錄</TabsTrigger>
          </TabsList>
          <TabsContent value="ocr">
            {ocrQ.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : (
              <DataTable
                columns={ocrCols}
                data={ocrQ.data ?? []}
                getRowId={(r) => String(r.ocr_job_id ?? r.id ?? '')}
              />
            )}
          </TabsContent>
          <TabsContent value="notif">
            {nq.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : (
              <DataTable
                columns={njCols}
                data={nq.data ?? []}
                getRowId={(r) => String(r.notification_job_id ?? '')}
              />
            )}
          </TabsContent>
          <TabsContent value="import">
            {iq.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : (
              <DataTable
                columns={ijCols}
                data={iq.data ?? []}
                getRowId={(r) => String(r.import_job_id ?? '')}
              />
            )}
          </TabsContent>
          <TabsContent value="audit">
            {aq.isLoading ? (
              <p className="text-muted-foreground text-sm">載入中…</p>
            ) : (
              <DataTable
                columns={auditCols}
                data={aq.data ?? []}
                getRowId={(r) => String(r.audit_log_id ?? r.id ?? '')}
              />
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
