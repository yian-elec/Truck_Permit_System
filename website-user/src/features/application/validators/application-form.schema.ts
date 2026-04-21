import { z } from 'zod'

export const applicationCoreSchema = z.object({
  reason_type: z.string().optional().or(z.literal('')),
  reason_detail: z.string().optional().or(z.literal('')),
  requested_start_at: z.string().optional().or(z.literal('')),
  requested_end_at: z.string().optional().or(z.literal('')),
  delivery_method: z.string().optional().or(z.literal('')),
})

export type ApplicationCoreValues = z.infer<typeof applicationCoreSchema>
