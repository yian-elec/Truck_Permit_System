import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiDataOrNull } from '@/shared/api/response-parser'

/** 與後端 RouteRequestStatusDTO 對齊（route-preview GET）。 */
export const routePreviewDataSchema = z.object({
  route_request_id: z.string().uuid(),
  application_id: z.string().uuid(),
  status: z.string(),
  origin_text: z.string(),
  destination_text: z.string(),
  geocode_failure_reason: z.string().nullable().optional(),
  requested_departure_at: z.string().nullable().optional(),
  vehicle_weight_ton: z.union([z.number(), z.string()]).nullable().optional(),
  vehicle_kind: z.string().nullable().optional(),
})

export type RoutePreviewData = z.infer<typeof routePreviewDataSchema>

export async function getRoutePreviewApi(applicationId: string): Promise<RoutePreviewData | null> {
  const { data } = await get<unknown>(endpoints.applicant.routePreview(applicationId))
  return parseApiDataOrNull(routePreviewDataSchema, data)
}
