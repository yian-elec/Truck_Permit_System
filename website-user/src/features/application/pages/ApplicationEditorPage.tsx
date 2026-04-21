import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { useMemo } from 'react'
import { FormProvider, useForm, type Resolver } from 'react-hook-form'
import { useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import {
  DELIVERY_METHOD_OPTIONS,
  REASON_TYPE_OPTIONS,
  normalizeDeliveryMethodCode,
} from '@/shared/constants/application-options'
import { usePageTitle, useConfirmLeave } from '@/shared/hooks'
import {
  PageContainer,
  SectionCard,
  Spinner,
  Button,
  Form,
  FormField,
  Input,
  Select,
} from '@/shared/ui'

import { useApplicationPermit } from '@/features/permit/hooks/useApplicationPermit'
import { useApplicationEditorPageModel } from '@/features/page-model/hooks/useApplicationEditorPageModel'
import { RouteRequestForm } from '@/features/routing/components/RouteRequestForm'
import { MissingItemsList } from '@/features/submission/components/MissingItemsList'
import { SubmissionCheckPanel } from '@/features/submission/components/SubmissionCheckPanel'
import { SubmitSection } from '@/features/submission/components/SubmitSection'
import { useSubmissionCheck } from '@/features/submission/hooks/useSubmissionCheck'
import { useSupplementRequests } from '@/features/supplement/hooks/useSupplementRequests'
import { ApplicationAttachmentsPanel } from '../components/ApplicationAttachmentsPanel'
import { ConsentClauseSection } from '../components/ConsentClauseSection'
import { useAttachments } from '@/features/attachment/hooks/useAttachments'
import { VehicleList } from '@/features/vehicle/components/VehicleList'

import { ApplicantProfileForm } from '../components/ApplicantProfileForm'
import { ApplicationSummaryCard } from '../components/ApplicationSummaryCard'
import { CompanyProfileForm } from '../components/CompanyProfileForm'
import { buildPatchApplicationBody } from '../lib/build-patch-application-body'
import { applicantProfileFromDto, companyProfileFromDto } from '../lib/profile-form-mappers'
import { useApplicationDetail } from '../hooks/useApplicationDetail'
import { usePatchApplication } from '../hooks/usePatchApplication'
import { useAcceptConsent } from '../hooks/useAcceptConsent'
import { applicationCoreSchema, type ApplicationCoreValues } from '../validators/application-form.schema'
import {
  applicantProfileFormSchema,
  companyProfileFormSchema,
  defaultApplicantProfileFormValues,
  defaultCompanyProfileFormValues,
  type ApplicantProfileFormValues,
  type CompanyProfileFormValues,
} from '../validators/profile-form.schema'

export function ApplicationEditorPage() {
  const { applicationId = '' } = useParams()
  usePageTitle(`編輯案件 ${applicationId}`)

  const detail = useApplicationDetail(applicationId)
  const supplementRequests = useSupplementRequests(applicationId)
  const permit = useApplicationPermit(applicationId)
  const submissionCheck = useSubmissionCheck(applicationId)
  const attachments = useAttachments(applicationId)
  const patch = usePatchApplication(applicationId)
  const consent = useAcceptConsent(applicationId)

  const reasonTypeSelectOptions = useMemo(() => {
    const current = detail.data?.reason_type?.trim()
    if (current && !REASON_TYPE_OPTIONS.some((o) => o.value === current)) {
      return [...REASON_TYPE_OPTIONS, { value: current, label: `${current}（目前值）` }]
    }
    return REASON_TYPE_OPTIONS
  }, [detail.data?.reason_type])

  const deliveryMethodSelectOptions = useMemo(() => {
    const current = normalizeDeliveryMethodCode(detail.data?.delivery_method)
    if (current && !DELIVERY_METHOD_OPTIONS.some((o) => o.value === current)) {
      return [...DELIVERY_METHOD_OPTIONS, { value: current, label: `${current}（目前值）` }]
    }
    return DELIVERY_METHOD_OPTIONS
  }, [detail.data?.delivery_method])

  const editorPageModelParams = useMemo(() => {
    const d = detail.data
    if (!d) return {}
    const items = (supplementRequests.data as { items?: unknown[] } | undefined)?.items
    const hasPendingSupplement =
      d.status === 'supplement_required' || (Array.isArray(items) && items.length > 0)
    // 自動規劃僅由審查／管理端觸發；申請端不反映已產生之路線方案。
    const hasActiveRoutePlan = false
    const hasIssuedPermitDocuments = Boolean(permit.isSuccess && permit.data)

    return {
      lifecycle_phase: d.status,
      has_active_route_plan: hasActiveRoutePlan,
      has_pending_supplement_request: hasPendingSupplement,
      has_issued_permit_documents: hasIssuedPermitDocuments,
    }
  }, [
    detail.data,
    supplementRequests.data,
    permit.isSuccess,
    permit.data,
  ])

  const pageModel = useApplicationEditorPageModel(
    applicationId,
    editorPageModelParams,
    Boolean(detail.data),
  )

  const coreForm = useForm<ApplicationCoreValues>({
    resolver: zodResolver(applicationCoreSchema),
    values: detail.data
      ? {
          reason_type: detail.data.reason_type ?? '',
          reason_detail: detail.data.reason_detail ?? '',
          requested_start_at: detail.data.requested_start_at ?? '',
          requested_end_at: detail.data.requested_end_at ?? '',
          delivery_method: normalizeDeliveryMethodCode(detail.data.delivery_method),
        }
      : {
          reason_type: '',
          reason_detail: '',
          requested_start_at: '',
          requested_end_at: '',
          delivery_method: '',
        },
  })

  const applicantForm = useForm<ApplicantProfileFormValues>({
    resolver: zodResolver(applicantProfileFormSchema) as Resolver<ApplicantProfileFormValues>,
    values: detail.data
      ? applicantProfileFromDto(detail.data.applicant)
      : defaultApplicantProfileFormValues(),
  })

  const companyForm = useForm<CompanyProfileFormValues>({
    resolver: zodResolver(companyProfileFormSchema) as Resolver<CompanyProfileFormValues>,
    values: detail.data ? companyProfileFromDto(detail.data.company) : defaultCompanyProfileFormValues(),
  })

  const dirty =
    coreForm.formState.isDirty ||
    applicantForm.formState.isDirty ||
    companyForm.formState.isDirty
  useConfirmLeave(dirty)

  const handleSaveAll = async () => {
    const [coreOk, applicantOk, companyOk] = await Promise.all([
      coreForm.trigger(),
      applicantForm.trigger(),
      companyForm.trigger(),
    ])
    if (!coreOk || !applicantOk || !companyOk) {
      toast.error('請修正表單錯誤後再儲存')
      return
    }
    const body = buildPatchApplicationBody(
      coreForm.getValues(),
      applicantForm.getValues(),
      companyForm.getValues(),
    )
    if (!body.patch && !body.profiles) {
      toast.message('沒有變更可儲存')
      return
    }
    patch.mutate(body, {
      onSuccess: () => {
        toast.success('已儲存')
        coreForm.reset(coreForm.getValues())
        applicantForm.reset(applicantForm.getValues())
        companyForm.reset(companyForm.getValues())
      },
      onError: (e) => toast.error(getErrorMessage(e)),
    })
  }

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

  const check = submissionCheck.data

  return (
    <PageContainer as="main" className="space-y-6 py-8">
      <ApplicationSummaryCard detail={detail.data} />

      {pageModel.data?.sections?.length ? (
        <SectionCard title="編輯區塊（頁面模型）">
          <ul className="list-inside list-disc text-sm text-muted-foreground">
            {pageModel.data.sections
              .slice()
              .sort((a, b) => a.sort_order - b.sort_order)
              .map((s) => (
                <li key={s.section_code}>{s.section_code}</li>
              ))}
          </ul>
        </SectionCard>
      ) : null}

      <SectionCard
        title="案件資料"
        description="案件欄位與申請人／公司資料一併儲存。"
      >
        <FormProvider {...coreForm}>
          <Form className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField<ApplicationCoreValues>
                name="reason_type"
                label="申請事由類型"
                children={(field) => (
                  <Select
                    id={field.name}
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLSelectElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={field.onChange}
                    options={reasonTypeSelectOptions}
                    placeholder="請選擇申請事由"
                  />
                )}
              />
              <FormField<ApplicationCoreValues>
                name="delivery_method"
                label="送達方式"
                children={(field) => (
                  <Select
                    id={field.name}
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLSelectElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={field.onChange}
                    options={deliveryMethodSelectOptions}
                    placeholder="請選擇送達方式"
                  />
                )}
              />
            </div>
            <FormField<ApplicationCoreValues>
              name="reason_detail"
              label="事由說明（選填）"
              children={(field) => (
                <Input
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                />
              )}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField<ApplicationCoreValues>
                name="requested_start_at"
                label="許可起始（ISO 日期時間）"
                children={(field) => (
                  <Input
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLInputElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={field.onChange}
                  />
                )}
              />
              <FormField<ApplicationCoreValues>
                name="requested_end_at"
                label="許可結束（ISO 日期時間）"
                children={(field) => (
                  <Input
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLInputElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={field.onChange}
                  />
                )}
              />
            </div>
          </Form>
        </FormProvider>

        <div className="mt-6 space-y-6">
          <ApplicantProfileForm form={applicantForm} />
          <CompanyProfileForm form={companyForm} />
        </div>

        <Button type="button" className="mt-6" loading={patch.isPending} onClick={handleSaveAll}>
          儲存案件
        </Button>
      </SectionCard>

      <ConsentClauseSection consent={consent} />

      <VehicleList applicationId={applicationId} />

      <ApplicationAttachmentsPanel applicationId={applicationId} attachments={attachments.data} />

      <RouteRequestForm applicationId={applicationId} />

      <SubmissionCheckPanel data={check} />
      {check?.missing_reason_codes?.length ? (
        <SectionCard title="無法送件原因">
          <MissingItemsList items={check.missing_reason_codes} />
        </SectionCard>
      ) : null}
      <SubmitSection applicationId={applicationId} />
    </PageContainer>
  )
}
