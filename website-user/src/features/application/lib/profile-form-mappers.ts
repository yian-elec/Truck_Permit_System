import type { ApplicantProfileDTO, CompanyProfileDTO } from '../types/application-dto.schema'
import {
  defaultApplicantProfileFormValues,
  defaultCompanyProfileFormValues,
  type ApplicantProfileFormValues,
  type CompanyProfileFormValues,
} from '../validators/profile-form.schema'

function str(v: string | null | undefined): string {
  return v ?? ''
}

export function applicantProfileFromDto(dto: ApplicantProfileDTO | null | undefined): ApplicantProfileFormValues {
  if (!dto) return defaultApplicantProfileFormValues()
  return {
    name: str(dto.name),
    id_no: str(dto.id_no),
    gender: str(dto.gender),
    email: str(dto.email),
    mobile: str(dto.mobile),
    phone_area: str(dto.phone_area),
    phone_no: str(dto.phone_no),
    phone_ext: str(dto.phone_ext),
    address_county: str(dto.address_county),
    address_district: str(dto.address_district),
    address_detail: str(dto.address_detail),
  }
}

export function companyProfileFromDto(dto: CompanyProfileDTO | null | undefined): CompanyProfileFormValues {
  if (!dto) return defaultCompanyProfileFormValues()
  return {
    company_name: str(dto.company_name),
    tax_id: str(dto.tax_id),
    principal_name: str(dto.principal_name),
    contact_name: str(dto.contact_name),
    contact_mobile: str(dto.contact_mobile),
    contact_phone: str(dto.contact_phone),
    address: str(dto.address),
  }
}
