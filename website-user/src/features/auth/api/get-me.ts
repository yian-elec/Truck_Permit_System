import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseApiData } from '@/shared/api/response-parser'

const meSchema = z.object({
  user_id: z.string(),
  account_type: z.string(),
  status: z.string(),
  display_name: z.string(),
  email: z.string(),
  mfa_enabled: z.boolean(),
})

export type MeResponse = z.infer<typeof meSchema>

export async function getMeApi(): Promise<MeResponse> {
  const { data } = await get<unknown>(endpoints.auth.me)
  return parseApiData(meSchema, data)
}
