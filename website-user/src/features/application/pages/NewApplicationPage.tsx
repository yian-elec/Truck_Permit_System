import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { z } from 'zod'

import { getErrorMessage } from '@/shared/api/api-error'
import {
  APPLICANT_TYPE_VALUES,
  REASON_TYPE_VALUES,
  DELIVERY_METHOD_VALUES,
  APPLICANT_TYPE_OPTIONS,
  REASON_TYPE_OPTIONS,
  DELIVERY_METHOD_OPTIONS,
} from '@/shared/constants/application-options'
import { routePaths } from '@/shared/constants/route-paths'
import { Button, Form, FormField, Input, PageContainer, SectionCard, Select } from '@/shared/ui'

import { ApplicationFlowStepper } from '../components/ApplicationFlowStepper'
import { useCreateApplication } from '../hooks/useCreateApplication'

function localDatetimeToIso(local: string): string {
  const d = new Date(local)
  if (Number.isNaN(d.getTime())) {
    throw new Error('Invalid date')
  }
  return d.toISOString()
}

const schema = z.object({
  applicant_type: z.enum(APPLICANT_TYPE_VALUES),
  reason_type: z.enum(REASON_TYPE_VALUES),
  reason_detail: z.string().optional(),
  requested_start_at: z.string().min(1),
  requested_end_at: z.string().min(1),
  delivery_method: z.enum(DELIVERY_METHOD_VALUES),
})

type Values = z.infer<typeof schema>

export function NewApplicationPage() {
  const navigate = useNavigate()
  const create = useCreateApplication()
  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: {
      applicant_type: 'natural_person',
      reason_type: 'public_work',
      reason_detail: '',
      requested_start_at: '',
      requested_end_at: '',
      delivery_method: 'online',
    },
  })

  const onSubmit = (values: Values) => {
    try {
      const requested_start_at = localDatetimeToIso(values.requested_start_at)
      const requested_end_at = localDatetimeToIso(values.requested_end_at)
      const reason_detail = values.reason_detail?.trim()

      create.mutate(
        {
          applicant_type: values.applicant_type,
          reason_type: values.reason_type,
          ...(reason_detail ? { reason_detail } : {}),
          requested_start_at,
          requested_end_at,
          delivery_method: values.delivery_method,
          source_channel: 'web',
        },
        {
          onSuccess: (res) => {
            toast.success('已建立案件')
            navigate(routePaths.applicantApplicationEdit(res.application_id), { replace: true })
          },
          onError: (e) => toast.error(getErrorMessage(e)),
        },
      )
    } catch (e) {
      toast.error(getErrorMessage(e))
    }
  }

  return (
    <PageContainer as="main" className="max-w-lg space-y-6 py-8">
      <ApplicationFlowStepper phase="new" />
      <div>
        <h1 className="text-2xl font-semibold">建立案件</h1>
        <p className="text-sm text-muted-foreground">建立一筆新的草稿案件，建立後可於編輯頁填寫完整資料。</p>
      </div>
      <SectionCard>
        <FormProvider {...form}>
          <Form onSubmit={form.handleSubmit(onSubmit)}>
            <FormField<Values>
              name="applicant_type"
              label="申請人類型"
              children={(field) => (
                <Select
                  id={field.name}
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLSelectElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                  options={APPLICANT_TYPE_OPTIONS}
                />
              )}
            />
            <FormField<Values>
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
                  options={REASON_TYPE_OPTIONS}
                />
              )}
            />
            <FormField<Values>
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
            <FormField<Values>
              name="requested_start_at"
              label="許可期間起"
              description="本地日期時間（儲存為 UTC ISO-8601）。"
              children={(field) => (
                <Input
                  type="datetime-local"
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                />
              )}
            />
            <FormField<Values>
              name="requested_end_at"
              label="許可期間迄"
              children={(field) => (
                <Input
                  type="datetime-local"
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                />
              )}
            />
            <FormField<Values>
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
                  options={DELIVERY_METHOD_OPTIONS}
                  placeholder="請選擇送達方式"
                />
              )}
            />
            <Button type="submit" className="mt-4 w-full" loading={create.isPending}>
              建立案件並開始填寫
            </Button>
          </Form>
        </FormProvider>
      </SectionCard>
    </PageContainer>
  )
}
