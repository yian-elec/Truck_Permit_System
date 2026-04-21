import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const applicationSummarySchema = z.object({
  application_id: z.string(),
  application_no: z.string(),
  status: z.string(),
  applicant_type: z.string(),
  updated_at: z.string(),
})

const schema = z.object({
  applications: z.array(applicationSummarySchema),
})

export type ApplicationSummary = z.infer<typeof applicationSummarySchema>
export type MyApplicationsPayload = z.infer<typeof schema>

export async function getMyApplicationsApi(): Promise<MyApplicationsPayload> {
  const { data } = await get<unknown>(endpoints.applicant.applications)
  return parseApiData(schema, data)
}
