import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get, post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const jobSchema = z.object({
  import_job_id: z.string().uuid(),
  status: z.string(),
  message: z.string().nullable().optional(),
})

export async function requestKmlImport(sourceDescription: string) {
  const { data } = await post<unknown>(endpoints.admin.mapImportsKml, {
    source_description: sourceDescription,
  })
  return parseResponse(jobSchema, data)
}

export async function getImportJob(importJobId: string) {
  const { data } = await get<unknown>(endpoints.admin.mapImportJob(importJobId))
  return data as Record<string, unknown>
}
