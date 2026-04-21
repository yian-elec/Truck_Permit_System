import { z } from 'zod'

/** 後端 ApplicantProfileDTO（JSON 之 UUID／日期皆為字串） */
export const applicantProfileSchema = z
  .object({
    name: z.string(),
    id_no: z.string().nullish(),
    gender: z.string().nullish(),
    email: z.string().nullish(),
    mobile: z.string().nullish(),
    phone_area: z.string().nullish(),
    phone_no: z.string().nullish(),
    phone_ext: z.string().nullish(),
    address_county: z.string().nullish(),
    address_district: z.string().nullish(),
    address_detail: z.string().nullish(),
  })
  .passthrough()

/** 後端 CompanyProfileDTO */
export const companyProfileSchema = z
  .object({
    company_name: z.string().nullish(),
    tax_id: z.string().nullish(),
    principal_name: z.string().nullish(),
    contact_name: z.string().nullish(),
    contact_mobile: z.string().nullish(),
    contact_phone: z.string().nullish(),
    address: z.string().nullish(),
  })
  .passthrough()

export const vehicleDtoSchema = z
  .object({
    vehicle_id: z.string(),
    application_id: z.string(),
    plate_no: z.string(),
    vehicle_kind: z.string(),
    gross_weight_ton: z.union([z.string(), z.number()]).nullish(),
    license_valid_until: z.string().nullish(),
    trailer_plate_no: z.string().nullish(),
    is_primary: z.boolean(),
    created_at: z.string(),
    updated_at: z.string(),
  })
  .passthrough()

export const checklistItemSchema = z
  .object({
    checklist_id: z.string(),
    item_code: z.string(),
    item_name: z.string(),
    is_required: z.boolean(),
    is_satisfied: z.boolean(),
    source: z.string(),
    note: z.string().nullish(),
  })
  .passthrough()

export const attachmentSummarySchema = z
  .object({
    attachment_id: z.string(),
    attachment_type: z.string(),
    file_id: z.string(),
    original_filename: z.string(),
    mime_type: z.string(),
    size_bytes: z.number(),
    status: z.string(),
    ocr_status: z.string(),
    uploaded_by: z.string().nullish(),
    uploaded_at: z.string(),
  })
  .passthrough()

export const statusHistoryEntrySchema = z
  .object({
    history_id: z.string(),
    from_status: z.string().nullish(),
    to_status: z.string(),
    changed_by: z.string().nullish(),
    reason: z.string().nullish(),
    created_at: z.string(),
  })
  .passthrough()

/** 後端 ApplicationDetailDTO */
export const applicationDetailSchema = z
  .object({
    application_id: z.string(),
    application_no: z.string(),
    status: z.string(),
    applicant_type: z.string(),
    reason_type: z.string(),
    reason_detail: z.string().nullish(),
    requested_start_at: z.string(),
    requested_end_at: z.string(),
    delivery_method: z.string(),
    source_channel: z.string(),
    applicant_user_id: z.string().nullish(),
    consent_accepted_at: z.string().nullish(),
    submitted_at: z.string().nullish(),
    version: z.number(),
    created_at: z.string(),
    updated_at: z.string(),
    applicant: applicantProfileSchema.nullish(),
    company: companyProfileSchema.nullish(),
    vehicles: z.array(vehicleDtoSchema),
    checklist: z.array(checklistItemSchema),
    attachments: z.array(attachmentSummarySchema),
    status_history: z.array(statusHistoryEntrySchema),
  })
  .passthrough()

/** 後端 ApplicationEditModelDTO */
export const applicationEditModelSchema = z.object({
  detail: applicationDetailSchema,
})

/** UC-APP-02 PatchApplicationInputDTO */
export const patchApplicationInputSchema = z.object({
  reason_type: z.string().optional(),
  reason_detail: z.string().nullish().optional(),
  requested_start_at: z.string().optional(),
  requested_end_at: z.string().optional(),
  delivery_method: z.string().optional(),
})

/** UC-APP-02 PatchApplicationProfilesInputDTO */
export const patchApplicationProfilesSchema = z.object({
  applicant: applicantProfileSchema.optional(),
  company: companyProfileSchema.optional(),
})

/** HTTP PATCH body：PatchApplicationRequestDTO */
export const patchApplicationRequestSchema = z.object({
  patch: patchApplicationInputSchema.optional(),
  profiles: patchApplicationProfilesSchema.optional(),
})

export type ApplicantProfileDTO = z.infer<typeof applicantProfileSchema>
export type CompanyProfileDTO = z.infer<typeof companyProfileSchema>
export type ApplicationDetailDTO = z.infer<typeof applicationDetailSchema>
export type ApplicationEditModelDTO = z.infer<typeof applicationEditModelSchema>
export type PatchApplicationInput = z.infer<typeof patchApplicationInputSchema>
export type PatchApplicationRequestBody = z.infer<typeof patchApplicationRequestSchema>
