import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const dataSchema = z.object({
  application_id: z.string(),
  status: z.string(),
  message: z.string().optional(),
})

export type SupplementResponseBody = {
  supplement_request_id: string
  note?: string
  patch?: Record<string, unknown>
  profiles?: {
    applicant?: Record<string, unknown>
    company?: Record<string, unknown>
  }
}

export type SupplementResponsePayload = z.infer<typeof dataSchema>

export async function postSupplementResponseApi(
  applicationId: string,
  body: SupplementResponseBody,
): Promise<SupplementResponsePayload> {
  const { data } = await post<unknown>(endpoints.applicant.supplementResponse(applicationId), body)
  return parseApiData(dataSchema, data)
}
