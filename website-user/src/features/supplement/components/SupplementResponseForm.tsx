import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useMemo } from 'react'
import { FormProvider, useForm, useWatch } from 'react-hook-form'
import type { Ref } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import { routePaths } from '@/shared/constants/route-paths'
import { Button, Form, FormField, Input, SectionCard, Select } from '@/shared/ui'

import type { SupplementRequestsList } from '../api/get-supplement-requests'
import { useSupplementResponse } from '../hooks/useSupplementResponse'
import { supplementResponseSchema, type SupplementResponseValues } from '../validators/supplement-form.schema'

function openSupplementItems(requests: SupplementRequestsList | null | undefined) {
  const items = requests?.items ?? []
  return items.filter((i) => {
    const st = 'status' in i && typeof i.status === 'string' ? i.status : 'open'
    return st === 'open'
  })
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

  const openItems = useMemo(() => openSupplementItems(requests ?? null), [requests])

  const form = useForm<SupplementResponseValues>({
    resolver: zodResolver(supplementResponseSchema),
    defaultValues: {
      supplement_request_id: '',
      note: '',
    },
  })

  const selectedId = useWatch({ control: form.control, name: 'supplement_request_id' }) as string
  const selected = openItems.find((i) => i.request_id === selectedId)

  useEffect(() => {
    if (openItems.length === 0) {
      form.setValue('supplement_request_id', '')
      return
    }
    const preferred =
      defaultRequestId && openItems.some((i) => i.request_id === defaultRequestId)
        ? defaultRequestId
        : openItems[0].request_id
    const current = form.getValues('supplement_request_id')
    if (!current || !openItems.some((i) => i.request_id === current)) {
      form.setValue('supplement_request_id', preferred)
    }
  }, [openItems, defaultRequestId, form])

  /** 尚有待回覆補件才顯示表單；全部完成後不占版面 */
  if (openItems.length === 0) {
    return null
  }

  const selectOptions = openItems.map((it) => ({
    value: it.request_id,
    label: it.title,
  }))

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
                onSuccess: (data) => {
                  const nextStatus = data.status
                  if (nextStatus === 'resubmitted') {
                    toast.success('已送出。案件已重新進入審查，請等候處理。')
                  } else {
                    toast.success('已送出本案補件；仍有其他待完成的補件時，請繼續回覆。')
                  }
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
            description="僅列出尚未完成的補件；完成全部後將重新送出審查。"
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
          {selected ? (
            <div className="border-border mt-3 rounded-md border bg-muted/30 px-3 py-3 text-sm">
              <p className="text-muted-foreground text-xs font-medium">補件說明</p>
              {selected.description ? (
                <p className="mt-2 whitespace-pre-wrap text-foreground">{selected.description}</p>
              ) : (
                <p className="text-muted-foreground mt-2">（此補件未附說明正文）</p>
              )}
            </div>
          ) : null}
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
