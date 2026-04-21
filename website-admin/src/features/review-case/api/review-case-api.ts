import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'
import type { PageModelResult } from '@/shared/types/page-model'

const loose = z.record(z.string(), z.unknown())

const reviewPageSchema = z.object({
  application: loose,
  route_plan: loose.nullable().optional(),
  ocr_summary: loose.nullable().optional(),
  decisions: z.array(loose),
  comments: z.array(loose),
  supplement_requests: z.array(loose),
})

export type ReviewPageData = z.infer<typeof reviewPageSchema>

export async function getReviewApplication(applicationId: string): Promise<ReviewPageData> {
  const { data } = await get<unknown>(endpoints.review.application(applicationId))
  return parseResponse(reviewPageSchema, data)
}

const pageModelSchema = z.object({
  page_kind: z.string(),
  contract_version_major: z.number(),
  application_id: z.union([z.string().uuid(), z.null()]).optional(),
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

export async function getReviewPageModel(
  applicationId: string,
  includePermitSection = true,
): Promise<PageModelResult> {
  const { data } = await get<unknown>(endpoints.pageModel.reviewApplication(applicationId), {
    params: { include_permit_section: includePermitSection },
  })
  return parseResponse(pageModelSchema, data) as PageModelResult
}
