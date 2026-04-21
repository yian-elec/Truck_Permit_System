import { z } from 'zod'

import { emailSchema } from '@/shared/validators/common'
import { passwordSchema } from '@/shared/validators/auth'

export const registerFormSchema = z.object({
  display_name: z.string().trim().min(1, 'Required'),
  email: emailSchema,
  mobile: z.string().trim().min(8, 'Enter a valid mobile'),
  password: passwordSchema,
})

export type RegisterFormValues = z.infer<typeof registerFormSchema>
