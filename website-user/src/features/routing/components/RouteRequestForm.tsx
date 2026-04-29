import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { useEffect, useRef } from 'react'
import { FormProvider, useForm, type Resolver } from 'react-hook-form'
import { toast } from 'sonner'

import { VEHICLE_KIND_OPTIONS } from '@/shared/constants/application-options'
import { Button, Form, FormField, Input, SectionCard, Select, Spinner } from '@/shared/ui'
import { routeRequestFormSchema, type RouteRequestFormValues } from '@/shared/validators/routing'

import { useCreateRouteRequest } from '../hooks/useCreateRouteRequest'
import { useRoutePreview } from '../hooks/useRoutePreview'
import { ROUTE_REQUEST_FORM_DEFAULTS, routePreviewToFormValues } from '../lib/route-preview-to-form'


function isoToLocalDatetime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function RouteRequestForm({ applicationId }: { applicationId: string }) {
  const preview = useRoutePreview(applicationId)
  const create = useCreateRouteRequest(applicationId)
  const syncedRouteRequestId = useRef<string | null>(null)

  const form = useForm<RouteRequestFormValues>({
    resolver: zodResolver(routeRequestFormSchema) as Resolver<RouteRequestFormValues>,
    defaultValues: ROUTE_REQUEST_FORM_DEFAULTS,
  })

  useEffect(() => {
    syncedRouteRequestId.current = null
  }, [applicationId])

  useEffect(() => {
    if (!preview.isSuccess) return
    if (preview.data == null) {
      syncedRouteRequestId.current = null
      return
    }
    const rid = preview.data.route_request_id
    if (syncedRouteRequestId.current === rid) return
    syncedRouteRequestId.current = rid
    form.reset(routePreviewToFormValues(preview.data))
  }, [preview.isSuccess, preview.data, form])

  return (
    <FormProvider {...form}>
      <Form
        onSubmit={form.handleSubmit((values) => {
          const depDate = new Date(values.requested_departure_at)
          const body = {
            ...values,
            requested_departure_at: Number.isNaN(depDate.getTime())
              ? values.requested_departure_at
              : depDate.toISOString(),
          }
          create.mutate(body, {
            onSuccess: () => toast.success('路線已儲存'),
            onError: () => toast.error('路線儲存失敗'),
          })
        })}
      >
        <SectionCard
          title="路線申請"
          description={
            preview.isSuccess && preview.data
              ? '已載入您上次儲存的起迄與車輛條件；修改後再送出會更新路線申請。'
              : undefined
          }
        >
          {preview.isPending ? (
            <div className="mb-4 flex items-center gap-2 text-muted-foreground text-sm">
              <Spinner />
              <span>載入已儲存的路線資料…</span>
            </div>
          ) : null}
          <div className="space-y-4">
            <FormField<RouteRequestFormValues>
              name="origin_text"
              label="起點"
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
            <FormField<RouteRequestFormValues>
              name="destination_text"
              label="終點"
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
            <FormField<RouteRequestFormValues>
              name="requested_departure_at"
              label="預計出發時間"
              children={(field) => (
                <Input
                  type="datetime-local"
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={isoToLocalDatetime(String(field.value ?? ''))}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                />
              )}
            />
            <FormField<RouteRequestFormValues>
              name="vehicle_weight_ton"
              label="車重（公噸）"
              children={(field) => (
                <Input
                  type="number"
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                />
              )}
            />
            <FormField<RouteRequestFormValues>
              name="vehicle_kind"
              label="車種"
              children={(field) => (
                <Select
                  id={field.name}
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLSelectElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                  options={VEHICLE_KIND_OPTIONS}
                  placeholder="請選擇車種"
                />
              )}
            />
            <Button type="submit" loading={create.isPending}>
              儲存路線
            </Button>
          </div>
        </SectionCard>
      </Form>
    </FormProvider>
  )
}
