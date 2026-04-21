import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'
import type { PageModelResult } from '@/shared/types/page-model'

const pageModelSchema = z.object({
  page_kind: z.string(),
  contract_version_major: z.number(),
  application_id: z.string().uuid().nullable().optional(),
  sections: z.array(
    z.object({
      section_code: z.string(),
      sort_order: z.number(),
      is_required_for_render: z.boolean(),
      feed_roles: z.array(z.string()),
      prerequisite_section_codes: z.array(z.string()),
    }),
  ),
  payload_by_section: z.record(z.string(), z.unknown()),
})

const reviewDashboardSchema = z.object({
  total_open_tasks: z.number(),
  pending_assignment_tasks: z.number(),
  in_review_tasks: z.number(),
  closed_tasks_in_window: z.number(),
})

export async function getAdminDashboardModel(): Promise<PageModelResult> {
  const { data } = await get<unknown>(endpoints.pageModel.adminDashboard)
  return parseResponse(pageModelSchema, data) as PageModelResult
}

export async function getReviewDashboardCounts() {
  const { data } = await get<unknown>(endpoints.review.dashboard)
  return parseResponse(reviewDashboardSchema, data)
}
