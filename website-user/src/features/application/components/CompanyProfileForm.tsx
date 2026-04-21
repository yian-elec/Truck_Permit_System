import type * as React from 'react'
import type { UseFormReturn } from 'react-hook-form'
import { FormProvider } from 'react-hook-form'

import { FormField, Input, SectionCard } from '@/shared/ui'

import type { CompanyProfileFormValues } from '../validators/profile-form.schema'

export function CompanyProfileForm({ form }: { form: UseFormReturn<CompanyProfileFormValues> }) {
  return (
    <FormProvider {...form}>
      <SectionCard title="公司資料" description="法人／團體申請人。">
        <div className="grid gap-4 sm:grid-cols-2">
          <FormField<CompanyProfileFormValues>
            name="company_name"
            label="公司名稱"
            className="sm:col-span-2"
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
          <FormField<CompanyProfileFormValues>
            name="tax_id"
            label="統一編號"
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
          <FormField<CompanyProfileFormValues>
            name="principal_name"
            label="負責人姓名"
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
          <FormField<CompanyProfileFormValues>
            name="contact_name"
            label="聯絡人姓名"
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
          <FormField<CompanyProfileFormValues>
            name="contact_mobile"
            label="聯絡人手機"
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
          <FormField<CompanyProfileFormValues>
            name="contact_phone"
            label="聯絡人電話"
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
          <FormField<CompanyProfileFormValues>
            name="address"
            label="地址"
            className="sm:col-span-2"
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
      </SectionCard>
    </FormProvider>
  )
}
