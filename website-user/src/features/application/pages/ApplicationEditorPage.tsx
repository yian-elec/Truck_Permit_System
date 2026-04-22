import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { useEffect, useMemo } from 'react'
import { FormProvider, useForm, useWatch, type Resolver } from 'react-hook-form'
import { Link, Navigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import {
  DELIVERY_METHOD_OPTIONS,
  REASON_TYPE_OPTIONS,
  normalizeDeliveryMethodCode,
} from '@/shared/constants/application-options'
import { routePaths } from '@/shared/constants/route-paths'
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

import { RouteRequestForm } from '@/features/routing/components/RouteRequestForm'
import { MissingItemsList } from '@/features/submission/components/MissingItemsList'
import { useSubmissionCheck } from '@/features/submission/hooks/useSubmissionCheck'
import { ApplicationAttachmentsPanel } from '../components/ApplicationAttachmentsPanel'
import { useAttachments } from '@/features/attachment/hooks/useAttachments'
import { VehicleList } from '@/features/vehicle/components/VehicleList'

import { ApplicantProfileForm } from '../components/ApplicantProfileForm'
import { ApplicationConsentSummarySection } from '../components/ApplicationConsentSummarySection'
import { ApplicationFlowStepper } from '../components/ApplicationFlowStepper'
import { ApplicationSummaryCard } from '../components/ApplicationSummaryCard'
import { CompanyProfileForm } from '../components/CompanyProfileForm'
import { isApplicantApplicationEditableStatus } from '../lib/application-edit-access'
import { buildPatchApplicationBody } from '../lib/build-patch-application-body'
import {
  filterDisplayMissingReasonCodes,
  isLocalProfileCompleteForSubmit,
} from '../lib/local-profile-readiness'
import { requiresCompanyProfileSection } from '../lib/applicant-type-ui'
import { applicantProfileFromDto, companyProfileFromDto } from '../lib/profile-form-mappers'
import { useApplicationDetail } from '../hooks/useApplicationDetail'
import { usePatchApplication } from '../hooks/usePatchApplication'
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
  const submissionCheck = useSubmissionCheck(applicationId)
  const attachments = useAttachments(applicationId)
  const patch = usePatchApplication(applicationId)

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

  const showCompany = requiresCompanyProfileSection(detail.data?.applicant_type)

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

  const watchedCore = useWatch({ control: coreForm.control })
  const watchedApplicant = useWatch({ control: applicantForm.control })
  const watchedCompany = useWatch({ control: companyForm.control })

  useEffect(() => {
    if (!detail.data) return
    if (!dirty) return
    const t = window.setTimeout(() => {
      void (async () => {
        const coreOk = await coreForm.trigger()
        const apOk = await applicantForm.trigger()
        const coOk = showCompany ? await companyForm.trigger() : true
        if (!coreOk || !apOk || !coOk) return
        const body = buildPatchApplicationBody(
          coreForm.getValues(),
          applicantForm.getValues(),
          companyForm.getValues(),
        )
        if (!body.patch && !body.profiles) return
        patch.mutate(body, {
          onSuccess: () => {
            coreForm.reset(coreForm.getValues())
            applicantForm.reset(applicantForm.getValues())
            companyForm.reset(companyForm.getValues())
          },
          onError: (e) => toast.error(getErrorMessage(e)),
        })
      })()
    }, 2000)
    return () => window.clearTimeout(t)
    // 依欄位變更與 dirty 觸發延遲儲存；watch* 讓逐字輸入會重置 timer
  }, [dirty, watchedCore, watchedApplicant, watchedCompany, detail.data, showCompany, applicationId])

  const handleSaveAll = async () => {
    const coreOk = await coreForm.trigger()
    const applicantOk = await applicantForm.trigger()
    const companyOk = showCompany ? await companyForm.trigger() : true
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
        toast.success('已儲存草稿')
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

  if (!isApplicantApplicationEditableStatus(detail.data.status)) {
    return <Navigate to={routePaths.applicantApplication(applicationId)} replace />
  }

  const check = submissionCheck.data
  const localProfileComplete = isLocalProfileCompleteForSubmit(
    detail.data.applicant_type,
    (watchedApplicant as ApplicantProfileFormValues) ?? applicantForm.getValues(),
    (watchedCompany as CompanyProfileFormValues) ?? companyForm.getValues(),
  )
  const displayMissingCodes = filterDisplayMissingReasonCodes(
    check?.missing_reason_codes,
    localProfileComplete,
  )
  const displayMissingCount = displayMissingCodes.length
  const isDraft = detail.data.status === 'draft'
  const isSupplementMode = detail.data.status === 'supplement_required'
  const previewHref = routePaths.applicantApplicationEditPreview(applicationId)
  const showPreviewCta = isDraft
  const showSave = true

  return (
    <PageContainer as="main" className="space-y-6 pb-28 pt-8">
      <ApplicationFlowStepper phase="edit" />

      <ApplicationSummaryCard detail={detail.data} />

      <div id="section-application-core" className="scroll-mt-24">
        <SectionCard
          title="案件資料"
          description="基本欄位與申請人資料一併儲存；公司資料僅限法人／團體申請時填寫。"
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
            {showCompany ? <CompanyProfileForm form={companyForm} /> : null}
          </div>
        </SectionCard>
      </div>

      <div id="section-vehicles" className="scroll-mt-24">
        <VehicleList applicationId={applicationId} />
      </div>

      <div id="section-attachments" className="scroll-mt-24">
        <ApplicationAttachmentsPanel applicationId={applicationId} attachments={attachments.data} />
      </div>

      <div id="section-route" className="scroll-mt-24">
        <RouteRequestForm applicationId={applicationId} />
      </div>

      {isDraft && applicationId ? <ApplicationConsentSummarySection applicationId={applicationId} /> : null}

      {isDraft && displayMissingCount > 0 ? (
        <SectionCard title="送件前檢查：尚缺項目">
          <p className="mb-2 text-sm text-muted-foreground">
            共 {displayMissingCount} 項；補齊後請前往預覽確認。申辦同意書可於本頁或預覽頁開啟視窗、勾選並按「確認」完成。表單會約 2 秒後自動儲存草稿，亦可手按「儲存草稿」。
          </p>
          <MissingItemsList page="edit" items={displayMissingCodes} applicationId={applicationId} />
        </SectionCard>
      ) : null}

      <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/80">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-muted-foreground">
            {isDraft && displayMissingCount > 0
              ? `目前尚缺 ${displayMissingCount} 項`
              : isDraft
                ? '可前往預覽並送件'
                : isSupplementMode
                  ? '待補件：請儲存變更，並至「補件」完成回覆。'
                  : null}
            {isDraft && !check?.can_submit ? ' · 目前不可送件' : null}
          </div>
          <div className="flex flex-wrap gap-2">
            {showSave ? (
              <Button type="button" loading={patch.isPending} onClick={handleSaveAll}>
                儲存草稿
              </Button>
            ) : null}
            {showPreviewCta ? (
              <Button type="button" variant="default" asChild>
                <Link to={previewHref}>前往預覽確認</Link>
              </Button>
            ) : null}
          </div>
        </div>
      </div>
    </PageContainer>
  )
}
