import type { AxiosInstance, AxiosResponse } from 'axios'
import axios from 'axios'

import { ApiError } from '@/shared/api/api-error'
import { isApiEnvelope } from '@/shared/api/envelope'
import { storageKeys } from '@/shared/constants/storage-keys'
import { logger } from '@/shared/lib/logger'
import { storage } from '@/shared/lib/storage'

function unwrapEnvelope<T>(response: AxiosResponse<T>): AxiosResponse<T> {
  const body = response.data as unknown
  if (!isApiEnvelope(body)) {
    return response
  }
  if (body.error != null) {
    throw new ApiError({
      message: body.error.message ?? 'Request failed',
      status: response.status,
      code: body.error.code,
      details: body,
    })
  }
  return { ...response, data: body.data as T }
}

/** 登入／註冊／MFA 等「未帶 token 的認證請求」若回 401，不觸發強制登出。 */
function isPublicAuthRequest(url: string): boolean {
  const u = url.toLowerCase()
  return (
    u.includes('/auth/login') ||
    u.includes('/auth/register') ||
    u.includes('/auth/mfa/verify') ||
    u.includes('/auth/refresh')
  )
}

function clearClientSession(): void {
  storage.remove(storageKeys.authToken)
  storage.remove(storageKeys.authSessionId)
  try {
    sessionStorage.removeItem(storageKeys.mfaChallengeId)
  } catch {
    /* ignore */
  }
}

function redirectToLoginIfNeeded(): void {
  const path = window.location.pathname
  if (path === '/login' || path === '/mfa') return
  window.location.assign('/login')
}

export function applyInterceptors(client: AxiosInstance): void {
  client.interceptors.request.use(
    (config) => {
      const token = storage.get(storageKeys.authToken)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error),
  )

  client.interceptors.response.use(
    (response) => unwrapEnvelope(response),
    (error) => {
      logger.debug('API error', error)

      if (axios.isAxiosError(error)) {
        const status = error.response?.status
        const url = String(error.config?.url ?? '')
        if (status === 401 && !isPublicAuthRequest(url)) {
          clearClientSession()
          redirectToLoginIfNeeded()
        }
      }

      if (error?.response?.data && isApiEnvelope(error.response.data)) {
        const env = error.response.data
        if (env.error != null) {
          return Promise.reject(
            new ApiError({
              message: env.error.message ?? error.message ?? 'Request failed',
              status: error.response?.status,
              code: env.error.code,
              details: env,
            }),
          )
        }
      }
      return Promise.reject(ApiError.fromUnknown(error))
    },
  )
}
