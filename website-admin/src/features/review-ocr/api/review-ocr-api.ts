import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const ocrSchema = z.object({
  application_id: z.string().uuid(),
  ocr_summary: z.record(z.string(), z.unknown()),
})

export async function getOcrSummary(applicationId: string) {
  const { data } = await get<unknown>(endpoints.review.ocrSummary(applicationId))
  return parseResponse(ocrSchema, data)
}
