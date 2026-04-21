import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.object({
  route_request_id: z.string(),
  application_id: z.string(),
  status: z.string(),
  origin_text: z.string().optional(),
  destination_text: z.string().optional(),
}).passthrough()

export type RouteRequestBody = {
  origin_text: string
  destination_text: string
  requested_departure_at: string
  vehicle_weight_ton: number
  vehicle_kind: string
}

export async function createRouteRequestApi(
  applicationId: string,
  body: RouteRequestBody,
): Promise<unknown> {
  const { data } = await post<unknown>(endpoints.applicant.routeRequest(applicationId), body)
  return parseApiData(schema, data)
}
