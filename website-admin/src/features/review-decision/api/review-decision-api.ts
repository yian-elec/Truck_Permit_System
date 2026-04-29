import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get, post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const decisionSchema = z.object({
  decision_id: z.string().uuid(),
  application_id: z.string().uuid(),
  decision_type: z.string(),
  selected_candidate_id: z.string().uuid().nullable().optional(),
  override_id: z.string().uuid().nullable().optional(),
  approved_start_at: z.string().nullable().optional(),
  approved_end_at: z.string().nullable().optional(),
  reason: z.string(),
  decided_by: z.string().uuid(),
  decided_at: z.string(),
  created_at: z.string(),
})

export type DecisionSummary = z.infer<typeof decisionSchema>

export async function listDecisions(applicationId: string) {
  const { data } = await get<unknown>(endpoints.review.decisions(applicationId))
  return parseResponse(z.array(decisionSchema), data)
}

export async function requestSupplement(
  applicationId: string,
  body: {
    title: string
    message: string
    deadline_at: string | null
    decision_reason: string
  },
) {
  const { data } = await post<unknown>(endpoints.review.supplement(applicationId), body)
  return parseResponse(
    z.object({
      supplement_request_id: z.string().uuid(),
      decision_id: z.string().uuid(),
      application_status: z.string(),
    }),
    data,
  )
}

export async function approveApplication(
  applicationId: string,
  body: {
    reason: string
    approved_start_at: string | null
    approved_end_at: string | null
    selected_candidate_id: string | null
    override_id: string | null
  },
) {
  const { data } = await post<unknown>(endpoints.review.approve(applicationId), body)
  return parseResponse(
    z.object({
      decision_id: z.string().uuid(),
      application_status: z.string(),
    }),
    data,
  )
}

export async function rejectApplication(applicationId: string, body: { reason: string }) {
  const { data } = await post<unknown>(endpoints.review.reject(applicationId), body)
  return parseResponse(
    z.object({
      decision_id: z.string().uuid(),
      application_status: z.string(),
    }),
    data,
  )
}
