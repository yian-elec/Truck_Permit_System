import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

import type { HandlingUnitsPayload } from '../types/public-service.types'

const unitSchema = z.object({
  name: z.string().optional(),
  phone: z.string().optional(),
  address: z.string().optional(),
})

const schema = z.object({
  units: z.array(unitSchema),
})

export async function getHandlingUnitsApi(): Promise<HandlingUnitsPayload> {
  const { data } = await get<unknown>(endpoints.publicService.handlingUnits)
  return parseApiData(schema, data)
}
