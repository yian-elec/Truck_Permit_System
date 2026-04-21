import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.object({
  download_url: z.string(),
  expires_at: z.string().optional(),
})

export async function getAttachmentDownloadUrlApi(
  applicationId: string,
  attachmentId: string,
): Promise<{ download_url: string; expires_at?: string }> {
  const { data } = await post<unknown>(
    endpoints.applicant.attachmentDownloadUrl(applicationId, attachmentId),
    {},
  )
  return parseApiData(schema, data)
}
