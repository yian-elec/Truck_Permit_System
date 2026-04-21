/** 申請端固定附件欄位（attachment_type 代碼；僅行車執照為必傳，其餘選傳） */
export const APPLICATION_ATTACHMENT_SLOTS = [
  {
    code: 'vehicle_license_copy',
    title: '行車執照影本（拖車使用證）',
    description:
      '依行車執照應定檢日前有效（檢驗）日期內核准通行。',
    required: true,
  },
  {
    code: 'engineering_contract_or_order',
    title: '工程合約書或訂購單',
    description: '',
    required: false,
  },
  {
    code: 'waste_site_consent',
    title: '棄土場同意書暨棄土流向證明',
    description: '',
    required: false,
  },
  {
    code: 'other_power_of_attorney',
    title: '其他(委託書)',
    description: '',
    required: false,
  },
] as const
