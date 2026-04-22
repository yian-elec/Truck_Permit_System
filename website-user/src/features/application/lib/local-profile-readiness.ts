import type { ApplicantProfileFormValues, CompanyProfileFormValues } from '../validators/profile-form.schema'

/** 對齊後端 ApplicantProfile.minimum_complete_for_natural_person */
function isNaturalMin(a: ApplicantProfileFormValues): boolean {
  if (!(a.name || '').trim()) return false
  if (!(a.id_no || '').trim()) return false
  if (!(a.email || '').trim() && !(a.mobile || '').trim()) return false
  return true
}

/** 對齊後端 CompanyProfile.minimum_complete_for_company */
function isCompanyMin(c: CompanyProfileFormValues): boolean {
  if (!(c.company_name || '').trim() || !(c.tax_id || '').trim()) return false
  if (!(c.contact_mobile || '').trim() && !(c.contact_phone || '').trim()) return false
  return true
}

/**
 * 與 Application._profile_complete 前端鏡像，供「尚缺申請人資料」在填妥表單後立即自 UI 隱藏（未按儲存亦同）。
 */
export function isLocalProfileCompleteForSubmit(
  applicantType: string | null | undefined,
  applicant: ApplicantProfileFormValues,
  company: CompanyProfileFormValues,
): boolean {
  const t = (applicantType || '').toLowerCase()
  if (t === 'natural_person' || t === 'government') {
    return isNaturalMin(applicant)
  }
  if (t === 'company') {
    return isCompanyMin(company)
  }
  if (t === 'other') {
    return isNaturalMin(applicant) || isCompanyMin(company)
  }
  return isNaturalMin(applicant)
}

export function filterDisplayMissingReasonCodes(
  codes: string[] | undefined,
  localProfileComplete: boolean,
): string[] {
  if (!codes?.length) return []
  if (localProfileComplete) {
    return codes.filter((c) => c !== 'incomplete_profile')
  }
  return codes
}
