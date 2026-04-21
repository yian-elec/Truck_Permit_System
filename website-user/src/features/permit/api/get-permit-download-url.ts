import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.object({
  download_url: z.string(),
  expires_at: z.string().optional(),
})

export async function getPermitDownloadUrlApi(
  applicationId: string,
  body: { document_id?: string } = {},
): Promise<{ download_url: string; expires_at?: string }> {
  const { data } = await post<unknown>(endpoints.applicant.permitDownloadUrl(applicationId), body)
  return parseApiData(schema, data)
}
