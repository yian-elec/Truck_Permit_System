import type { AxiosInstance } from 'axios'

import { logger } from '@/shared/lib/logger'
import { getAccessToken } from '@/shared/lib/auth-token'

export function applyInterceptors(client: AxiosInstance): void {
  client.interceptors.request.use(
    (config) => {
      const token = getAccessToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error),
  )

  client.interceptors.response.use(
    (response) => response,
    (error) => {
      logger.debug('API error', error)
      return Promise.reject(error)
    },
  )
}
