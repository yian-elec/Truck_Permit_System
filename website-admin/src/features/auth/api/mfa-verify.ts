import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

export const mfaVerifyResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string().optional().nullable(),
  session_id: z.string().uuid(),
  access_token_jti: z.string(),
  refresh_token_jti: z.string().optional().nullable(),
  expires_at: z.string(),
})

export type MfaVerifyResponse = z.infer<typeof mfaVerifyResponseSchema>

export async function mfaVerifyApi(body: { challenge_id: string; code: string }): Promise<MfaVerifyResponse> {
  const { data } = await post<unknown>(endpoints.auth.mfaVerify, {
    challenge_id: body.challenge_id,
    code: body.code.trim(),
  })
  return parseResponse(mfaVerifyResponseSchema, data)
}
