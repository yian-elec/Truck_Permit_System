import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

export const loginDataSchema = z.object({
  mfa_required: z.boolean(),
  access_token: z.string().nullable().optional(),
  refresh_token: z.string().nullable().optional(),
  session_id: z.string().uuid().nullable().optional(),
  access_token_jti: z.string().nullable().optional(),
  refresh_token_jti: z.string().nullable().optional(),
  challenge_id: z.string().uuid().nullable().optional(),
  expires_at: z.string().nullable().optional(),
})

export type LoginData = z.infer<typeof loginDataSchema>

export type LoginRequestBody = {
  login_mode: 'password'
  identifier: string
  password: string
}

export async function loginApi(body: LoginRequestBody): Promise<LoginData> {
  const { data } = await post<unknown>(endpoints.auth.login, {
    ...body,
    identifier: body.identifier.trim(),
  })
  return parseApiData(loginDataSchema, data)
}
