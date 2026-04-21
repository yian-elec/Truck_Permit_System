import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useMemo, type Ref } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import { routePaths } from '@/shared/constants/route-paths'
import { Button, Form, FormField, Input, SectionCard, Select } from '@/shared/ui'

import type { SupplementRequestsList } from '../api/get-supplement-requests'
import { useSupplementResponse } from '../hooks/useSupplementResponse'
import { supplementResponseSchema, type SupplementResponseValues } from '../validators/supplement-form.schema'

function buildSelectLabel(it: {
  title: string
  description?: string | null
}): string {
  const raw = (it.description ?? '').trim().replace(/\s+/g, ' ')
  const preview = raw.length > 100 ? `${raw.slice(0, 97)}…` : raw
  if (preview) {
    return `${it.title} — ${preview}`
  }
  return it.title
}

export function SupplementResponseForm({
  applicationId,
  requests,
  defaultRequestId,
}: {
  applicationId: string
  requests?: SupplementRequestsList | null
  defaultRequestId?: string
}) {
  const navigate = useNavigate()
  const submit = useSupplementResponse(applicationId)
  const items = requests?.items ?? []

  const selectOptions = useMemo(
    () =>
      items.map((it) => ({
        value: it.request_id,
        label: buildSelectLabel(it),
      })),
    [items],
  )

  const form = useForm<SupplementResponseValues>({
    resolver: zodResolver(supplementResponseSchema),
    defaultValues: {
      supplement_request_id: '',
      note: '',
    },
  })

  useEffect(() => {
    if (items.length === 0) {
      form.setValue('supplement_request_id', '')
      return
    }
    const preferred =
      defaultRequestId && items.some((i) => i.request_id === defaultRequestId)
        ? defaultRequestId
        : items[0].request_id
    const current = form.getValues('supplement_request_id')
    if (!current || !items.some((i) => i.request_id === current)) {
      form.setValue('supplement_request_id', preferred)
    }
  }, [items, defaultRequestId, form])

  if (items.length === 0) {
    return (
      <SectionCard title="補件回覆">
        <p className="text-sm text-muted-foreground">
          目前沒有可回覆的補件單；請待機關發出補件通知後再送出回覆。
        </p>
      </SectionCard>
    )
  }

  return (
    <SectionCard title="補件回覆">
      <FormProvider {...form}>
        <Form
          onSubmit={form.handleSubmit((values) => {
            const note = values.note?.trim()
            submit.mutate(
              {
                supplement_request_id: values.supplement_request_id,
                ...(note ? { note } : {}),
              },
              {
                onSuccess: () => {
                  toast.success('已送出補件回覆')
                  navigate(routePaths.applicantApplication(applicationId))
                },
                onError: (e) => toast.error(getErrorMessage(e)),
              },
            )
          })}
        >
          <FormField<SupplementResponseValues>
            name="supplement_request_id"
            label="要回覆的補件"
            description="請依補件說明選擇對應通知（無需自行輸入 ID）。"
            required
            children={(field) => (
              <Select
                id={String(field.name)}
                name={field.name}
                ref={field.ref as Ref<HTMLSelectElement>}
                value={String(field.value ?? '')}
                onBlur={field.onBlur}
                onChange={(e) => field.onChange(e.target.value)}
                options={selectOptions}
                placeholder="請選擇補件通知"
              />
            )}
          />
          <FormField<SupplementResponseValues>
            name="note"
            label="說明（選填）"
            children={(field) => (
              <Input
                name={field.name}
                ref={field.ref as Ref<HTMLInputElement>}
                value={String(field.value ?? '')}
                onBlur={field.onBlur}
                onChange={field.onChange}
                placeholder="可簡述已補交之檔案或修正內容"
              />
            )}
          />
          <Button type="submit" className="mt-4" loading={submit.isPending}>
            送出補件回覆
          </Button>
        </Form>
      </FormProvider>
    </SectionCard>
  )
}
