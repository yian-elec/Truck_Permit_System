import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

export const loginResponseSchema = z.object({
  mfa_required: z.boolean(),
  challenge_id: z.string().optional().nullable(),
  access_token: z.string().optional().nullable(),
  refresh_token: z.string().optional().nullable(),
  session_id: z.string().uuid().optional().nullable(),
  access_token_jti: z.string().optional().nullable(),
  refresh_token_jti: z.string().optional().nullable(),
  expires_at: z.string().optional().nullable(),
})

export type LoginResponse = z.infer<typeof loginResponseSchema>

export async function loginApi(body: { email: string; password: string }): Promise<LoginResponse> {
  const { data } = await post<unknown>(endpoints.auth.login, {
    login_mode: 'password',
    identifier: body.email.trim(),
    password: body.password,
  })
  return parseResponse(loginResponseSchema, data)
}
