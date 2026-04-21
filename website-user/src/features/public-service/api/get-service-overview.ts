import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

import type { ServiceOverview } from '../types/public-service.types'

const schema = z.object({
  service_code: z.string(),
  display_name: z.string(),
  description: z.string(),
  api_version: z.string(),
})

export async function getServiceOverviewApi(): Promise<ServiceOverview> {
  const { data } = await get<unknown>(endpoints.publicService.overview)
  return parseApiData(schema, data)
}
