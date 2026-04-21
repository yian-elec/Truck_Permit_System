import { z } from 'zod'

/** 自然人申請人表單（對齊 ApplicantProfileDTO；僅姓名、電子郵件、通訊地址為必填） */
export const applicantProfileFormSchema = z.object({
  name: z.string().min(1, '請填姓名'),
  id_no: z.string(),
  gender: z.string(),
  email: z.string().min(1, '請填電子郵件').email('請填有效電子郵件'),
  mobile: z.string(),
  phone_area: z.string(),
  phone_no: z.string(),
  phone_ext: z.string(),
  address_county: z.string().min(1, '請選擇縣市'),
  address_district: z.string().min(1, '請選擇或填寫區'),
  address_detail: z.string().min(1, '請填寫地址'),
})

export type ApplicantProfileFormValues = z.infer<typeof applicantProfileFormSchema>

export const defaultApplicantProfileFormValues = (): ApplicantProfileFormValues => ({
  name: '',
  id_no: '',
  gender: '',
  email: '',
  mobile: '',
  phone_area: '',
  phone_no: '',
  phone_ext: '',
  address_county: '',
  address_district: '',
  address_detail: '',
})

/** 公司申請人表單（對齊 CompanyProfileDTO） */
export const companyProfileFormSchema = z.object({
  company_name: z.string(),
  tax_id: z.string(),
  principal_name: z.string(),
  contact_name: z.string(),
  contact_mobile: z.string(),
  contact_phone: z.string(),
  address: z.string(),
})

export type CompanyProfileFormValues = z.infer<typeof companyProfileFormSchema>

export const defaultCompanyProfileFormValues = (): CompanyProfileFormValues => ({
  company_name: '',
  tax_id: '',
  principal_name: '',
  contact_name: '',
  contact_mobile: '',
  contact_phone: '',
  address: '',
})
