import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get, post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

export type RoutePlanDetail = Record<string, unknown>

const ruleHitsSchema = z.object({
  route_plan_id: z.string().uuid(),
  hits: z.array(z.record(z.string(), z.unknown())),
})

export async function getRoutePlan(applicationId: string): Promise<RoutePlanDetail | null> {
  const { data } = await get<unknown>(endpoints.review.routePlan(applicationId))
  if (data == null) return null
  return data as RoutePlanDetail
}

export async function getRuleHits(applicationId: string) {
  const { data } = await get<unknown>(endpoints.review.routePlanRuleHits(applicationId))
  if (data == null) return null
  return parseResponse(ruleHitsSchema, data)
}

export async function selectCandidate(applicationId: string, candidateId: string): Promise<RoutePlanDetail> {
  const { data } = await post<unknown>(endpoints.review.routePlanSelectCandidate(applicationId), {
    candidate_id: candidateId,
  })
  return data as RoutePlanDetail
}

export async function overrideRoute(
  applicationId: string,
  body: { override_line_wkt: string; override_reason: string; base_candidate_id: string | null },
): Promise<RoutePlanDetail> {
  const { data } = await post<unknown>(endpoints.review.routePlanOverride(applicationId), body)
  return data as RoutePlanDetail
}

const replanOutSchema = z.object({ route_plan_id: z.string().uuid() })

export async function replanRoute(applicationId: string) {
  const { data } = await post<unknown>(endpoints.review.routePlanReplan(applicationId), {})
  return parseResponse(replanOutSchema, data)
}
