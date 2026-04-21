import { z } from 'zod'

export const mfaFormSchema = z.object({
  challenge_id: z.string().min(1),
  code: z.string().trim().length(6, 'Enter 6-digit code'),
})

export type MfaFormValues = z.infer<typeof mfaFormSchema>
