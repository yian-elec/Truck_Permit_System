import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.object({
  attachments: z.array(z.unknown()).optional(),
}).passthrough()

export async function getAttachmentsApi(applicationId: string): Promise<unknown> {
  const { data } = await get<unknown>(endpoints.applicant.attachments(applicationId))
  return parseApiData(schema, data)
}
