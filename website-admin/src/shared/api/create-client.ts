import axios from 'axios'

import { getApiBaseUrl } from '@/shared/config/get-api-base-url'

import { applyInterceptors } from './interceptors'

export function createApiClient() {
  const client = axios.create({
    baseURL: getApiBaseUrl() || undefined,
    timeout: 30_000,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  })

  applyInterceptors(client)
  return client
}
