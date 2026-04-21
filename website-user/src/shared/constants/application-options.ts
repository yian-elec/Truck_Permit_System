/**
 * 與後端 Application 領域對齊之表單選項（applicant_type / reason_type / delivery_method / vehicle_kind）。
 * applicant_type 須為 ApplicantTypeCode；reason_type 為非空字串（≤50），此處列常用代碼供 select 使用。
 * delivery_method 須為 DeliveryMethodCode（online | mail | counter | other）。
 * vehicle_kind：後端為 ≤50 字元之任意代碼；此處列常用車種（與 seed、路線 vehicle_profile.kind 慣例一致）。
 */

export type ApplicationFieldOption = { value: string; label: string }

export const APPLICANT_TYPE_OPTIONS: ApplicationFieldOption[] = [
  { value: 'natural_person', label: '自然人' },
  { value: 'company', label: '公司／法人' },
  { value: 'government', label: '政府機關' },
  { value: 'other', label: '其他' },
]

export const APPLICANT_TYPE_VALUES = APPLICANT_TYPE_OPTIONS.map((o) => o.value) as [
  string,
  ...string[],
]

/** 與後端 ReasonType（varchar≤50）相容：公共工程／民間工地／貨物運輸／其他 */
export const REASON_TYPE_OPTIONS: ApplicationFieldOption[] = [
  { value: 'public_work', label: '公共工程' },
  { value: 'private_site', label: '民間工地' },
  { value: 'cargo_transport', label: '貨物運輸' },
  { value: 'other', label: '其他' },
]

export const REASON_TYPE_VALUES = REASON_TYPE_OPTIONS.map((o) => o.value) as [string, ...string[]]

export const DELIVERY_METHOD_OPTIONS: ApplicationFieldOption[] = [
  { value: 'online', label: '線上／電子送達' },
  { value: 'mail', label: '郵寄' },
  { value: 'counter', label: '臨櫃' },
  { value: 'other', label: '其他' },
]

export const DELIVERY_METHOD_VALUES = DELIVERY_METHOD_OPTIONS.map((o) => o.value) as [
  string,
  ...string[],
]

/** 對齊後端 DeliveryMethod：已知代碼不分大小寫正規化為小寫；未知值保留 trim 後原文（供僅顯示 legacy）。 */
export function normalizeDeliveryMethodCode(raw: string | null | undefined): string {
  const s = (raw ?? '').trim()
  if (!s) return ''
  const lower = s.toLowerCase()
  if (DELIVERY_METHOD_OPTIONS.some((o) => o.value === lower)) return lower
  return s
}

export const VEHICLE_KIND_OPTIONS: ApplicationFieldOption[] = [
  { value: 'sand_truck', label: '砂石車' },
  { value: 'ready_mix_truck', label: '預拌混凝土車' },
  { value: 'general_hgv', label: '一般大貨車' },
  { value: 'special_vehicle', label: '特種車輛' },
  { value: 'other_power_of_attorney', label: '其他(委託書)' },
]

export const VEHICLE_KIND_VALUES = VEHICLE_KIND_OPTIONS.map((o) => o.value) as [string, ...string[]]
