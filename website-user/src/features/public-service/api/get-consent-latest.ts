import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

import type { ConsentLatest } from '../types/public-service.types'

const schema = z.object({
  version: z.string(),
  effective_at: z.string(),
  summary: z.string(),
  must_accept_before_submit: z.boolean(),
})

export async function getConsentLatestApi(): Promise<ConsentLatest> {
  const { data } = await get<unknown>(endpoints.publicService.consentLatest)
  return parseApiData(schema, data)
}
