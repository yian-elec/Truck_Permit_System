/** 與申請端附件欄位一致，供補件項目下拉選單與 API 代碼對齊 */
export const SUPPLEMENT_DOCUMENT_PRESETS = [
  {
    code: 'vehicle_license_copy',
    title: '行車執照影本（拖車使用證）',
  },
  {
    code: 'engineering_contract_or_order',
    title: '工程合約書或訂購單',
  },
  {
    code: 'waste_site_consent',
    title: '棄土場同意書暨棄土流向證明',
  },
  {
    code: 'other_power_of_attorney',
    title: '其他(委託書)',
  },
] as const

export type SupplementPresetCode = (typeof SUPPLEMENT_DOCUMENT_PRESETS)[number]['code']
