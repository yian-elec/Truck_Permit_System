import { z } from 'zod'

export const applicationPatchSchema = z.object({
  reason_type: z.string().optional(),
  reason_detail: z.string().optional(),
  requested_start_at: z.string().optional(),
  requested_end_at: z.string().optional(),
  delivery_method: z.string().optional(),
})
