import { z } from 'zod'

import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'
import { parseResponse } from '@/shared/api/response-parser'

const assignOutSchema = z.object({
  assignment_id: z.string().uuid(),
  target_user_id: z.string().uuid(),
  role_code: z.string(),
  scope_type: z.string().nullable().optional(),
  scope_id: z.string().nullable().optional(),
})

export async function assignRole(
  userId: string,
  body: { role_code: string; assignment_id: string; scope_type?: string | null; scope_id?: string | null },
) {
  const { data } = await post<unknown>(endpoints.admin.userRoles(userId), body)
  return parseResponse(assignOutSchema, data)
}
