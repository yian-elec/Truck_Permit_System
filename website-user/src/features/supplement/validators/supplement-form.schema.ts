import { z } from 'zod'

export const supplementResponseSchema = z.object({
  supplement_request_id: z.string().min(1, '請選擇要回覆的補件'),
  note: z.string().optional(),
})

export type SupplementResponseValues = z.infer<typeof supplementResponseSchema>
