import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { patch } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

import { patchApplicationRequestSchema, type PatchApplicationRequestBody } from '../types/application-dto.schema'

const patchResponseSchema = z.unknown()

export async function patchApplicationApi(
  applicationId: string,
  body: PatchApplicationRequestBody,
): Promise<unknown> {
  const parsed = patchApplicationRequestSchema.parse(body)
  const { data } = await patch<unknown>(endpoints.applicant.applicationDetail(applicationId), parsed)
  return parseApiData(patchResponseSchema, data)
}
