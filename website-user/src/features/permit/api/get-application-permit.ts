import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiDataOrNull } from '@/shared/api/response-parser'

const schema = z.object({
  permit_id: z.string(),
  permit_no: z.string(),
  application_id: z.string(),
  status: z.string(),
  approved_start_at: z.string().nullable().optional(),
  approved_end_at: z.string().nullable().optional(),
  route_summary_text: z.string().optional(),
}).passthrough()

export async function getApplicationPermitApi(applicationId: string): Promise<unknown | null> {
  const { data } = await get<unknown>(endpoints.applicant.permit(applicationId))
  return parseApiDataOrNull(schema, data)
}
