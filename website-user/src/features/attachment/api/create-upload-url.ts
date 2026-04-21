import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

/** 後端 PresignedUploadUrlOutputDTO */
export const presignedUploadUrlOutputSchema = z.object({
  upload_url: z.string(),
  object_key: z.string(),
  file_id: z.string(),
})

export type PresignedUploadUrlOutput = z.infer<typeof presignedUploadUrlOutputSchema>

export async function createUploadUrlApi(
  applicationId: string,
  body: { mime_type: string },
): Promise<PresignedUploadUrlOutput> {
  const { data } = await post<unknown>(endpoints.applicant.attachmentsUploadUrl(applicationId), body)
  return parseApiData(presignedUploadUrlOutputSchema, data)
}
