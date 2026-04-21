import { z } from 'zod'

import { passwordSchema } from '@/shared/validators/auth'
import { requiredStringSchema } from '@/shared/validators/common'

export const loginFormSchema = z.object({
  identifier: requiredStringSchema,
  password: passwordSchema,
})

export type LoginFormValues = z.infer<typeof loginFormSchema>
