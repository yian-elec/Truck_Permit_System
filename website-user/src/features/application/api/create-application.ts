import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.object({
  application_id: z.string(),
  application_no: z.string(),
  status: z.string(),
})

export type CreateApplicationBody = {
  applicant_type: string
  reason_type: string
  reason_detail?: string
  requested_start_at: string
  requested_end_at: string
  delivery_method: string
  source_channel: string
}

export type CreateApplicationResult = z.infer<typeof schema>

export async function createApplicationApi(
  body: CreateApplicationBody,
): Promise<CreateApplicationResult> {
  const { data } = await post<unknown>(endpoints.applicant.applications, body)
  return parseApiData(schema, data)
}
