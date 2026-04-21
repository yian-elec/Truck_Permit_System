import { zodResolver } from '@hookform/resolvers/zod'
import type * as React from 'react'
import { useMemo } from 'react'
import { FormProvider, useForm, type Resolver } from 'react-hook-form'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import { VEHICLE_KIND_OPTIONS } from '@/shared/constants/application-options'
import {
  Button,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Form,
  FormField,
  Input,
  Select,
} from '@/shared/ui'
import { vehicleFormSchema, type VehicleFormValues } from '@/shared/validators/vehicle'

import { useAddVehicle } from '../hooks/useAddVehicle'
import { usePatchVehicle } from '../hooks/usePatchVehicle'

export function VehicleFormDialog({
  applicationId,
  initial,
  triggerLabel = '新增車輛',
}: {
  applicationId: string
  initial?: Partial<VehicleFormValues> & { vehicle_id?: string }
  triggerLabel?: string
}) {
  const vehicleKindOptions = useMemo(() => {
    const current = initial?.vehicle_kind?.trim()
    if (current && !VEHICLE_KIND_OPTIONS.some((o) => o.value === current)) {
      return [...VEHICLE_KIND_OPTIONS, { value: current, label: `${current}（目前值）` }]
    }
    return VEHICLE_KIND_OPTIONS
  }, [initial?.vehicle_kind])

  const add = useAddVehicle(applicationId)
  const patch = usePatchVehicle(applicationId)
  const form = useForm<VehicleFormValues>({
    resolver: zodResolver(vehicleFormSchema) as Resolver<VehicleFormValues>,
    defaultValues: {
      plate_no: initial?.plate_no ?? '',
      vehicle_kind: initial?.vehicle_kind ?? 'general_hgv',
      gross_weight_ton: initial?.gross_weight_ton ?? 15,
      license_valid_until: initial?.license_valid_until
        ? String(initial.license_valid_until).trim().slice(0, 10)
        : '',
      trailer_plate_no: initial?.trailer_plate_no ?? '',
    },
  })

  const isEdit = Boolean(initial?.vehicle_id)

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm" type="button">
          {triggerLabel}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? '編輯車輛' : '新增車輛'}</DialogTitle>
        </DialogHeader>
        <FormProvider {...form}>
          <Form
            onSubmit={form.handleSubmit((values) => {
              if (isEdit && initial?.vehicle_id) {
                patch.mutate(
                  { vehicleId: initial.vehicle_id, body: values },
                  {
                    onSuccess: () => toast.success('已更新車輛'),
                    onError: (e) => toast.error(getErrorMessage(e)),
                  },
                )
              } else {
                add.mutate(values, {
                  onSuccess: () => toast.success('已新增車輛'),
                  onError: (e) => toast.error(getErrorMessage(e)),
                })
              }
            })}
          >
            <FormField<VehicleFormValues>
              name="plate_no"
              label="車牌號碼"
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
            <FormField<VehicleFormValues>
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
                  options={vehicleKindOptions}
                  placeholder="請選擇車種"
                />
              )}
            />
            <FormField<VehicleFormValues>
              name="gross_weight_ton"
              label="總重（公噸）"
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
            <FormField<VehicleFormValues>
              name="license_valid_until"
              label="行照有效日（選填）"
              description="格式 YYYY-MM-DD；無則留空。"
              children={(field) => (
                <Input
                  type="date"
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                />
              )}
            />
            <FormField<VehicleFormValues>
              name="trailer_plate_no"
              label="拖車車牌（選填）"
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
            <Button type="submit" className="mt-4 w-full" loading={add.isPending || patch.isPending}>
              儲存
            </Button>
          </Form>
        </FormProvider>
      </DialogContent>
    </Dialog>
  )
}
