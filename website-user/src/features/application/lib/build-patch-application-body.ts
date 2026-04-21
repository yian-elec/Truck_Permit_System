import type {
  ApplicantProfileDTO,
  CompanyProfileDTO,
  PatchApplicationRequestBody,
} from '../types/application-dto.schema'
import type { ApplicationCoreValues } from '../validators/application-form.schema'
import type { ApplicantProfileFormValues, CompanyProfileFormValues } from '../validators/profile-form.schema'

function emptyToNull(s: string): string | null {
  const t = s.trim()
  return t === '' ? null : t
}

function buildApplicantDto(values: ApplicantProfileFormValues): ApplicantProfileDTO {
  return {
    name: values.name.trim(),
    id_no: emptyToNull(values.id_no),
    gender: emptyToNull(values.gender),
    email: emptyToNull(values.email),
    mobile: emptyToNull(values.mobile),
    phone_area: emptyToNull(values.phone_area),
    phone_no: emptyToNull(values.phone_no),
    phone_ext: emptyToNull(values.phone_ext),
    address_county: emptyToNull(values.address_county),
    address_district: emptyToNull(values.address_district),
    address_detail: emptyToNull(values.address_detail),
  }
}

function buildCompanyDto(values: CompanyProfileFormValues): CompanyProfileDTO {
  return {
    company_name: emptyToNull(values.company_name),
    tax_id: emptyToNull(values.tax_id),
    principal_name: emptyToNull(values.principal_name),
    contact_name: emptyToNull(values.contact_name),
    contact_mobile: emptyToNull(values.contact_mobile),
    contact_phone: emptyToNull(values.contact_phone),
    address: emptyToNull(values.address),
  }
}

function hasCompanyPayload(values: CompanyProfileFormValues): boolean {
  return Object.values(values).some((v) => String(v).trim() !== '')
}

/**
 * 組出 PATCH `/applicant/applications/{id}` 請求體。
 * - `patch`：僅含要更新的主表欄位；空字串的選填欄位轉成略過或 null（reason_detail）。
 * - `profiles`：若自然人姓名非空則帶 applicant；若公司區塊任一有值則帶 company。
 */
export function buildPatchApplicationBody(
  core: ApplicationCoreValues,
  applicant: ApplicantProfileFormValues,
  company: CompanyProfileFormValues,
): PatchApplicationRequestBody {
  const patch: NonNullable<PatchApplicationRequestBody['patch']> = {}

  const reasonType = core.reason_type?.trim()
  if (reasonType) patch.reason_type = reasonType

  const rd = core.reason_detail?.trim()
  if (rd) patch.reason_detail = rd

  const start = core.requested_start_at?.trim()
  if (start) patch.requested_start_at = start

  const end = core.requested_end_at?.trim()
  if (end) patch.requested_end_at = end

  const delivery = core.delivery_method?.trim()
  if (delivery) patch.delivery_method = delivery

  const body: PatchApplicationRequestBody = {}

  if (Object.keys(patch).length > 0) {
    body.patch = patch
  }

  const profiles: NonNullable<PatchApplicationRequestBody['profiles']> = {}

  if (applicant.name.trim() !== '') {
    profiles.applicant = buildApplicantDto(applicant)
  }

  if (hasCompanyPayload(company)) {
    profiles.company = buildCompanyDto(company)
  }

  if (profiles.applicant || profiles.company) {
    body.profiles = profiles
  }

  return body
}
