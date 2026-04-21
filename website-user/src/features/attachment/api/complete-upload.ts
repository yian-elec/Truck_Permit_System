import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.unknown()

export type CompleteUploadBody = {
  file_id: string
  attachment_id: string
  attachment_type: string
  original_filename: string
  mime_type: string
  size_bytes: number
  checksum_sha256: string
  bucket_name: string
  object_key: string
  storage_provider: string
}

export async function completeUploadApi(
  applicationId: string,
  body: CompleteUploadBody,
): Promise<unknown> {
  const { data } = await post<unknown>(endpoints.applicant.attachmentsComplete(applicationId), body)
  return parseApiData(schema, data)
}
