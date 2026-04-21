import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const registerDataSchema = z.object({
  user_id: z.string().uuid(),
  display_name: z.string(),
  /** 與後端 RegisterApplicantOutputDTO 一致：可為 null */
  email: z.string().nullable().optional(),
  mobile: z.string().nullable().optional(),
  status: z.string(),
})

export type RegisterData = z.infer<typeof registerDataSchema>

export type RegisterRequestBody = {
  display_name: string
  email: string
  mobile: string
  password: string
}

export async function registerApi(body: RegisterRequestBody): Promise<RegisterData> {
  const { data } = await post<unknown>(endpoints.auth.register, body)
  return parseApiData(registerDataSchema, data)
}
