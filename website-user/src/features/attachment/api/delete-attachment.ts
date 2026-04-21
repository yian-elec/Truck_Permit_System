import { endpoints } from '@/shared/api/endpoints'
import { del } from '@/shared/api/request'

export async function deleteAttachmentApi(
  applicationId: string,
  attachmentId: string,
): Promise<void> {
  await del(endpoints.applicant.attachment(applicationId, attachmentId))
}
