import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const supplementItemSchema = z
  .object({
    request_id: z.string(),
    title: z.string(),
    description: z.string().nullish(),
    status: z.string().optional(),
    created_at: z.string(),
  })
  .passthrough()

/** 後端 SupplementRequestListDTO */
const schema = z
  .object({
    items: z.array(supplementItemSchema).optional(),
  })
  .passthrough()

export type SupplementRequestsList = z.infer<typeof schema>

export async function getSupplementRequestsApi(applicationId: string): Promise<SupplementRequestsList> {
  const { data } = await get<unknown>(endpoints.applicant.supplementRequests(applicationId))
  return parseApiData(schema, data)
}
