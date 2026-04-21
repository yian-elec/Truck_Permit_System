import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const eventSchema = z.object({
  at: z.string().optional(),
  kind: z.string().optional(),
  message: z.string().optional(),
}).passthrough()

const schema = z.object({
  events: z.array(eventSchema).optional(),
  items: z.array(z.unknown()).optional(),
}).passthrough()

export type TimelinePayload = z.infer<typeof schema>

export async function getTimelineApi(applicationId: string): Promise<TimelinePayload> {
  const { data } = await get<unknown>(endpoints.applicant.applicationTimeline(applicationId))
  return parseApiData(schema, data)
}
