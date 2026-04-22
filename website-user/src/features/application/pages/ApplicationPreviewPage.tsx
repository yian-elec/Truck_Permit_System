import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import {
  DELIVERY_METHOD_OPTIONS,
  REASON_TYPE_OPTIONS,
  VEHICLE_KIND_OPTIONS,
} from '@/shared/constants/application-options'
import { routePaths } from '@/shared/constants/route-paths'
import { usePageTitle } from '@/shared/hooks'
import { PageContainer, SectionCard, Spinner, Button } from '@/shared/ui'
import { formatDate } from '@/shared/utils/format-date'

import { useAttachments } from '@/features/attachment/hooks/useAttachments'
import { useRoutePreview } from '@/features/routing/hooks/useRoutePreview'
import { MissingItemsList } from '@/features/submission/components/MissingItemsList'
import { useSubmitApplication } from '@/features/submission/hooks/useSubmitApplication'
import { useSubmissionCheck } from '@/features/submission/hooks/useSubmissionCheck'

import { ApplicationFlowStepper } from '../components/ApplicationFlowStepper'
import { ApplicationSummaryCard } from '../components/ApplicationSummaryCard'
import { canPreviewSubmit, PreviewConsentPanel } from '../components/PreviewConsentPanel'
import { requiresCompanyProfileSection } from '../lib/applicant-type-ui'
import { useApplicationDetail } from '../hooks/useApplicationDetail'
import { useAcceptConsent } from '../hooks/useAcceptConsent'
import type { ApplicationDetailDTO } from '../types/application-dto.schema'

function optLabel(options: { value: string; label: string }[], value: string): string {
  return options.find((o) => o.value === value)?.label ?? value
}

function buildChecklistLines(c: ApplicationDetailDTO['checklist']) {
  return c
    .filter((i) => i.is_required)
    .map((i) => `${i.item_name}：${i.is_satisfied ? '已備' : '未備'}`)
}

export function ApplicationPreviewPage() {
  const { applicationId = '' } = useParams()
  const navigate = useNavigate()
  usePageTitle(`預覽確認 ${applicationId}`)

  const detail = useApplicationDetail(applicationId)
  const submissionCheck = useSubmissionCheck(applicationId)
  const attachments = useAttachments(applicationId)
  const routePreview = useRoutePreview(applicationId)
  const consent = useAcceptConsent(applicationId)
  const submit = useSubmitApplication(applicationId)

  if (detail.isLoading) {
    return (
      <PageContainer className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </PageContainer>
    )
  }

  if (!detail.data) {
    return <PageContainer>找不到案件</PageContainer>
  }

  const d = detail.data
  if (d.status !== 'draft') {
    return <Navigate to={routePaths.applicantApplication(applicationId)} replace />
  }

  const check = submissionCheck.data
  const checklistLines = buildChecklistLines(d.checklist ?? [])
  const showCompany = requiresCompanyProfileSection(d.applicant_type)
  const ap = d.applicant
  const co = d.company
  const consentOk = canPreviewSubmit(d.consent_accepted_at)
  const submitDisabled =
    submit.isPending ||
    !check?.can_submit ||
    !consentOk

  return (
    <PageContainer as="main" className="space-y-6 pb-28 pt-8">
      <ApplicationFlowStepper phase="preview" />

      <ApplicationSummaryCard detail={d} />

      <div id="section-preview-core" className="scroll-mt-24">
        <SectionCard title="案件基本資料">
        <dl className="grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-muted-foreground">申請事由類型</dt>
            <dd>{optLabel(REASON_TYPE_OPTIONS, d.reason_type)}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">送達方式</dt>
            <dd>{optLabel(DELIVERY_METHOD_OPTIONS, d.delivery_method)}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-muted-foreground">事由說明</dt>
            <dd>{d.reason_detail?.trim() || '—'}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">許可期間起</dt>
            <dd>{formatDate(d.requested_start_at)}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">許可期間迄</dt>
            <dd>{formatDate(d.requested_end_at)}</dd>
          </div>
        </dl>
        </SectionCard>
      </div>

      {ap ? (
        <div id="section-preview-applicant" className="scroll-mt-24">
        <SectionCard title="申請人資料">
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">姓名</dt>
              <dd>{ap.name || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">身分證字號</dt>
              <dd>{ap.id_no || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">性別</dt>
              <dd>{ap.gender || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">電子郵件</dt>
              <dd>{ap.email || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">行動電話</dt>
              <dd>{ap.mobile || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">室內電話</dt>
              <dd>
                {[ap.phone_area, ap.phone_no, ap.phone_ext].filter(Boolean).join(' ') || '—'}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-muted-foreground">通訊地址</dt>
              <dd>
                {[ap.address_county, ap.address_district, ap.address_detail].filter(Boolean).join(
                  '',
                ) || '—'}
              </dd>
            </div>
          </dl>
        </SectionCard>
        </div>
      ) : null}

      {showCompany && co ? (
        <SectionCard title="公司資料">
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div className="sm:col-span-2">
              <dt className="text-muted-foreground">公司名稱</dt>
              <dd>{co.company_name || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">統一編號</dt>
              <dd>{co.tax_id || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">負責人姓名</dt>
              <dd>{co.principal_name || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">聯絡人姓名</dt>
              <dd>{co.contact_name || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">聯絡人手機</dt>
              <dd>{co.contact_mobile || '—'}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">聯絡人電話</dt>
              <dd>{co.contact_phone || '—'}</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-muted-foreground">地址</dt>
              <dd>{co.address || '—'}</dd>
            </div>
          </dl>
        </SectionCard>
      ) : null}

      <div id="section-preview-vehicles" className="scroll-mt-24">
        <SectionCard title="車輛列表">
        {d.vehicles.length === 0 ? (
          <p className="text-sm text-muted-foreground">尚無車輛資料。</p>
        ) : (
          <ul className="space-y-2">
            {d.vehicles.map((v) => {
              const kindLabel =
                VEHICLE_KIND_OPTIONS.find((o) => o.value === v.vehicle_kind)?.label ?? v.vehicle_kind
              return (
                <li
                  key={v.vehicle_id}
                  className="rounded-md border border-border px-3 py-2 text-sm"
                >
                  <span className="font-medium">{v.plate_no}</span>
                  <span className="text-muted-foreground">
                    {' '}
                    · {kindLabel} · {v.gross_weight_ton ?? '—'} 噸
                  </span>
                </li>
              )
            })}
          </ul>
        )}
        </SectionCard>
      </div>

      <div id="section-preview-attachments" className="scroll-mt-24">
        <SectionCard title="附件上傳狀態">
        {attachments.isLoading ? (
          <Spinner />
        ) : (
          <ul className="list-inside list-disc text-sm text-muted-foreground">
            {checklistLines.length ? (
              checklistLines.map((line: string) => <li key={line}>{line}</li>)
            ) : (
              <li>無清單資料；已上傳 {d.attachments?.length ?? 0} 個檔案。</li>
            )}
          </ul>
        )}
        </SectionCard>
      </div>

      <div id="section-preview-route" className="scroll-mt-24">
        <SectionCard title="路線資料">
        {routePreview.isLoading ? (
          <Spinner />
        ) : routePreview.data ? (
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div className="sm:col-span-2">
              <dt className="text-muted-foreground">起點</dt>
              <dd>{routePreview.data.origin_text}</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-muted-foreground">終點</dt>
              <dd>{routePreview.data.destination_text}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">預計出發時間</dt>
              <dd>
                {routePreview.data.requested_departure_at
                  ? formatDate(routePreview.data.requested_departure_at)
                  : '—'}
              </dd>
            </div>
            {routePreview.data.geocode_failure_reason ? (
              <div className="sm:col-span-2 text-amber-600">
                地理編碼提醒：{routePreview.data.geocode_failure_reason}
              </div>
            ) : null}
          </dl>
        ) : (
          <p className="text-sm text-muted-foreground">尚未儲存路線。</p>
        )}
        </SectionCard>
      </div>

      {check?.missing_reason_codes?.length ? (
        <SectionCard title="送件前檢查：尚缺項目">
          <MissingItemsList page="preview" items={check.missing_reason_codes} applicationId={applicationId} />
        </SectionCard>
      ) : null}

      <PreviewConsentPanel consent={consent} consentAcceptedAt={d.consent_accepted_at} />

      {!consentOk ? (
        <p className="text-sm text-amber-600">尚未完成申辦同意書，無法送件</p>
      ) : null}

      <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/80">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-muted-foreground">
            {!check?.can_submit ? '目前不可送件（請先補齊欄位）' : '送件前請確認以上資料無誤'}
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" asChild>
              <Link to={routePaths.applicantApplicationEdit(applicationId)}>返回編輯</Link>
            </Button>
            <Button
              type="button"
              disabled={submitDisabled}
              loading={submit.isPending}
              onClick={() =>
                submit.mutate(undefined, {
                  onSuccess: () => {
                    toast.success('已送件')
                    void navigate(
                      routePaths.applicantApplicationSubmitComplete(applicationId),
                      { replace: true },
                    )
                  },
                  onError: (e) => toast.error(getErrorMessage(e)),
                })
              }
            >
              正式送件
            </Button>
          </div>
        </div>
      </div>
    </PageContainer>
  )
}
