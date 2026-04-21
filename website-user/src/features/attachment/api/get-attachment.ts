import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const schema = z.unknown()

export async function getAttachmentApi(
  applicationId: string,
  attachmentId: string,
): Promise<unknown> {
  const { data } = await get<unknown>(endpoints.applicant.attachment(applicationId, attachmentId))
  return parseApiData(schema, data)
}
