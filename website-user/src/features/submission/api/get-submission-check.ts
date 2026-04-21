import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

/** 後端 SubmissionCheckResultDTO */
const schema = z
  .object({
    can_submit: z.boolean(),
    missing_reason_codes: z.array(z.string()),
  })
  .passthrough()

export type SubmissionCheckResult = z.infer<typeof schema>

export async function getSubmissionCheckApi(applicationId: string): Promise<SubmissionCheckResult> {
  const { data } = await get<unknown>(endpoints.applicant.submissionCheck(applicationId))
  return parseApiData(schema, data)
}
