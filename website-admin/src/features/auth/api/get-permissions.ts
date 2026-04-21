import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { get } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const permissionsResponseSchema = z.object({
  permission_codes: z.array(z.string()),
})

export type PermissionsResponse = z.infer<typeof permissionsResponseSchema>

export async function getPermissionsApi(): Promise<string[]> {
  const { data } = await get<unknown>(endpoints.auth.permissions)
  const parsed = parseResponse(permissionsResponseSchema, data)
  return parsed.permission_codes
}
