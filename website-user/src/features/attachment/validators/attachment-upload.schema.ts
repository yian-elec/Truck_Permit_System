import { z } from 'zod'

export const attachmentUploadSchema = z.object({
  mime_type: z.string().min(1),
})
