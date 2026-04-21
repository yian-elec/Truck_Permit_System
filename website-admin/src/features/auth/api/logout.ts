import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'

export async function logoutApi(sessionId: string): Promise<void> {
  await post(endpoints.auth.logout, { session_id: sessionId })
}
