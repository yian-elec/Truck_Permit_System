import { z } from 'zod'

// 台灣身分證字號：1 字母 + 9 數字
const twIdNoRegex = /^[A-Z][12]\d{8}$/
// 台灣手機：09 開頭 10 碼，可含 - 或空格
const mobileRegex = /^09\d{2}[\s-]?\d{3}[\s-]?\d{3}$/
// 電話區碼：2~3 位數字
const phoneAreaRegex = /^\d{2,3}$/
// 電話號碼：6~8 位數字，可含 - 或空格
const phoneNoRegex = /^\d{3,4}[\s-]?\d{4}$/
// 統一編號：8 位數字
const taxIdRegex = /^\d{8}$/

/**
 * 自然人申請人表單
 */
export const applicantProfileFormSchema = z.object({
  name: z.string().min(1, '請填姓名'),
  id_no: z
    .string()
    .min(1, '請填身分證字號')
    .refine((v) => twIdNoRegex.test(v.toUpperCase()), '身分證字號格式不正確（應為 1 英文字母 + 9 數字）'),
  gender: z.string(),
  email: z
    .string()
    .min(1, '請填電子郵件')
    .email('電子郵件格式不正確'),
  mobile: z
    .string()
    .refine(
      (v) => v === '' || mobileRegex.test(v),
      '手機號碼格式不正確（應為 09 開頭 10 碼）',
    ),
  phone_area: z
    .string()
    .refine(
      (v) => v === '' || phoneAreaRegex.test(v),
      '區碼應為 2~3 位數字',
    ),
  phone_no: z
    .string()
    .refine(
      (v) => v === '' || phoneNoRegex.test(v),
      '電話號碼格式不正確',
    ),
  phone_ext: z
    .string()
    .refine(
      (v) => v === '' || /^\d{1,6}$/.test(v),
      '分機應為數字',
    ),
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

/** 公司申請人表單 */
export const companyProfileFormSchema = z.object({
  company_name: z.string(),
  tax_id: z
    .string()
    .refine(
      (v) => v === '' || taxIdRegex.test(v),
      '統一編號應為 8 位數字',
    ),
  principal_name: z.string(),
  contact_name: z.string(),
  contact_mobile: z
    .string()
    .refine(
      (v) => v === '' || mobileRegex.test(v),
      '手機號碼格式不正確（應為 09 開頭 10 碼）',
    ),
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
