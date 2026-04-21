import type * as React from 'react'
import type { UseFormReturn } from 'react-hook-form'
import { FormProvider } from 'react-hook-form'

import { districtsForCounty, TW_COUNTIES } from '@/shared/constants/tw-county-district'
import { FormField, Input, SectionCard, Select } from '@/shared/ui'

import type { ApplicantProfileFormValues } from '../validators/profile-form.schema'

const COUNTY_OPTIONS = TW_COUNTIES.map((c) => ({ value: c, label: c }))

const GENDER_OPTIONS = [
  { value: '', label: '不填' },
  { value: '男生', label: '男生' },
  { value: '女生', label: '女生' },
  { value: '其他', label: '其他' },
]

export function ApplicantProfileForm({ form }: { form: UseFormReturn<ApplicantProfileFormValues> }) {
  const county = form.watch('address_county')
  const districtList = county ? districtsForCounty(county) : null
  const districtOptions =
    districtList?.map((d) => ({
      value: d,
      label: d,
    })) ?? []

  return (
    <FormProvider {...form}>
      <SectionCard title="申請人資料" description="標示 * 為必填，其餘選填。">
        <div className="grid gap-4 sm:grid-cols-2">
          <FormField<ApplicantProfileFormValues>
            name="name"
            label="姓名"
            required
            className="sm:col-span-2"
            children={(field) => (
              <Input
                name={field.name}
                ref={field.ref as React.Ref<HTMLInputElement>}
                value={String(field.value ?? '')}
                onBlur={field.onBlur}
                onChange={field.onChange}
                autoComplete="name"
              />
            )}
          />
          <FormField<ApplicantProfileFormValues>
            name="id_no"
            label="身分證字號"
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
          <FormField<ApplicantProfileFormValues>
            name="gender"
            label="性別"
            children={(field) => (
              <Select
                id={field.name}
                name={field.name}
                ref={field.ref as React.Ref<HTMLSelectElement>}
                value={String(field.value ?? '')}
                onBlur={field.onBlur}
                onChange={field.onChange}
                options={GENDER_OPTIONS}
                placeholder="不填"
              />
            )}
          />
          <FormField<ApplicantProfileFormValues>
            name="email"
            label="電子郵件"
            required
            children={(field) => (
              <Input
                type="email"
                name={field.name}
                ref={field.ref as React.Ref<HTMLInputElement>}
                value={String(field.value ?? '')}
                onBlur={field.onBlur}
                onChange={field.onChange}
                autoComplete="email"
              />
            )}
          />
          <FormField<ApplicantProfileFormValues>
            name="mobile"
            label="行動電話"
            children={(field) => (
              <Input
                name={field.name}
                ref={field.ref as React.Ref<HTMLInputElement>}
                value={String(field.value ?? '')}
                onBlur={field.onBlur}
                onChange={field.onChange}
                autoComplete="tel-national"
              />
            )}
          />
          <div className="space-y-2 sm:col-span-2">
            <p className="text-sm font-medium leading-none">室內電話（選填）</p>
            <p className="text-xs text-muted-foreground">區碼、市話、分機同一區塊填寫。</p>
            <div className="grid gap-3 rounded-lg border border-border p-4 sm:grid-cols-[1fr_2fr_1fr]">
              <FormField<ApplicantProfileFormValues>
                name="phone_area"
                label="區碼"
                children={(field) => (
                  <Input
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLInputElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={field.onChange}
                    placeholder="例 02"
                    inputMode="numeric"
                  />
                )}
              />
              <FormField<ApplicantProfileFormValues>
                name="phone_no"
                label="電話號碼"
                children={(field) => (
                  <Input
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLInputElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={field.onChange}
                    placeholder="市話號碼"
                    inputMode="tel"
                  />
                )}
              />
              <FormField<ApplicantProfileFormValues>
                name="phone_ext"
                label="分機"
                children={(field) => (
                  <Input
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLInputElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={field.onChange}
                    placeholder="分機"
                    inputMode="numeric"
                  />
                )}
              />
            </div>
          </div>

          <div className="space-y-4 sm:col-span-2">
            <p className="text-sm font-medium leading-none">
              通訊地址<span className="text-destructive"> *</span>
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField<ApplicantProfileFormValues>
                name="address_county"
                label="縣市"
                required
                children={(field) => (
                  <Select
                    id={field.name}
                    name={field.name}
                    ref={field.ref as React.Ref<HTMLSelectElement>}
                    value={String(field.value ?? '')}
                    onBlur={field.onBlur}
                    onChange={(e) => {
                      field.onChange(e)
                      form.setValue('address_district', '')
                    }}
                    options={COUNTY_OPTIONS}
                    placeholder="請選擇縣市"
                  />
                )}
              />
              {districtList ? (
                <FormField<ApplicantProfileFormValues>
                  name="address_district"
                  label="區"
                  required
                  children={(field) => (
                    <Select
                      id={field.name}
                      name={field.name}
                      ref={field.ref as React.Ref<HTMLSelectElement>}
                      value={String(field.value ?? '')}
                      onBlur={field.onBlur}
                      onChange={field.onChange}
                      options={districtOptions}
                      placeholder="請選擇區"
                    />
                  )}
                />
              ) : (
                <FormField<ApplicantProfileFormValues>
                  name="address_district"
                  label="區（鄉鎮市區）"
                  required
                  children={(field) => (
                    <Input
                      name={field.name}
                      ref={field.ref as React.Ref<HTMLInputElement>}
                      value={String(field.value ?? '')}
                      onBlur={field.onBlur}
                      onChange={field.onChange}
                      placeholder={county ? '請輸入鄉鎮市區' : '請先選縣市'}
                      disabled={!county}
                    />
                  )}
                />
              )}
            </div>
            <FormField<ApplicantProfileFormValues>
              name="address_detail"
              label="街道門牌等詳細地址"
              required
              className="sm:col-span-2"
              children={(field) => (
                <Input
                  name={field.name}
                  ref={field.ref as React.Ref<HTMLInputElement>}
                  value={String(field.value ?? '')}
                  onBlur={field.onBlur}
                  onChange={field.onChange}
                  autoComplete="street-address"
                />
              )}
            />
          </div>
        </div>
      </SectionCard>
    </FormProvider>
  )
}
