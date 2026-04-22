/**
 * 法人与团体申请时顯示公司资料區塊；其他類型僅顯示申請人主檔欄位。
 * 團體以 `other` 與 v2 對齊；公司行號以 `company`。
 */
export function requiresCompanyProfileSection(applicantType: string | undefined | null): boolean {
  if (!applicantType) return false
  return applicantType === 'company' || applicantType === 'other'
}
