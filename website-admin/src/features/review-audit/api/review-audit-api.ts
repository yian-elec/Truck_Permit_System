import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const entrySchema = z.object({
  entry_type: z.string(),
  occurred_at: z.string(),
  payload: z.record(z.string(), z.unknown()),
})

export type AuditEntry = z.infer<typeof entrySchema>

export async function listAuditTrail(applicationId: string) {
  const { data } = await get<unknown>(endpoints.review.auditTrail(applicationId))
  return parseResponse(z.array(entrySchema), data)
}
