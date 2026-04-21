import { endpoints } from '@/shared/api/endpoints'
import { post } from '@/shared/api/request'

export async function logoutApi(): Promise<void> {
  await post(endpoints.auth.logout)
}
