import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const verifyMfaDataSchema = z.object({
  access_token: z.string(),
  session_id: z.string().optional(),
  access_token_jti: z.string().optional(),
  expires_at: z.string().optional(),
})

export type VerifyMfaData = z.infer<typeof verifyMfaDataSchema>

export type VerifyMfaRequestBody = {
  challenge_id: string
  code: string
}

export async function verifyMfaApi(body: VerifyMfaRequestBody): Promise<VerifyMfaData> {
  const { data } = await post<unknown>(endpoints.auth.verifyMfa, body)
  return parseApiData(verifyMfaDataSchema, data)
}
