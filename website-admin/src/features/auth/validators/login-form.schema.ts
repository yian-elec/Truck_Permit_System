import { z } from 'zod'

import { passwordSchema } from '@/shared/validators/auth'

/** 後端以 identifier 比對 username 或 email，不必強制為信箱格式。 */
export const loginFormSchema = z.object({
  email: z.string().trim().min(1, 'Required'),
  password: passwordSchema,
})

export type LoginFormValues = z.infer<typeof loginFormSchema>
