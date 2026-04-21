import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

/** 與 Application DownloadUrlOutputDTO 對齊之下載／預覽 URL */
const previewSchema = z.object({
  download_url: z.string(),
  expires_at: z.string().optional().nullable(),
})

export async function getAttachmentPreviewUrl(applicationId: string, attachmentId: string) {
  const { data } = await get<unknown>(endpoints.review.attachmentPreview(applicationId, attachmentId))
  return parseResponse(previewSchema, data)
}
