import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

import type { RequiredDocumentsPayload } from '../types/public-service.types'

const docSchema = z.object({
  id: z.string().optional(),
  title: z.string().optional(),
  description: z.string().optional(),
})

const schema = z.object({
  documents: z.array(docSchema),
})

export async function getRequiredDocumentsApi(): Promise<RequiredDocumentsPayload> {
  const { data } = await get<unknown>(endpoints.publicService.requiredDocuments)
  return parseApiData(schema, data)
}
