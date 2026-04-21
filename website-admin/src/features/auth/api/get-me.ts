import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

import type { AuthUser } from '../types/auth.types'

const meResponseSchema = z.object({
  user_id: z.string().uuid(),
  account_type: z.string(),
  status: z.string(),
  display_name: z.string(),
  email: z.string().nullable().optional(),
  mobile: z.string().nullable().optional(),
  mfa_enabled: z.boolean(),
  username: z.string().nullable().optional(),
})

export async function getMeApi(): Promise<AuthUser> {
  const { data } = await get<unknown>(endpoints.auth.me)
  const raw = parseResponse(meResponseSchema, data)
  return {
    id: raw.user_id,
    email: raw.email ?? '',
    displayName: raw.display_name,
  }
}
