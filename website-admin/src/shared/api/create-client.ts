import axios from 'axios'

import { appConfig } from '@/shared/config/app-config'

import { applyInterceptors } from './interceptors'

export function createApiClient() {
  const client = axios.create({
    baseURL: appConfig.apiBaseUrl || undefined,
    timeout: 30_000,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  })

  applyInterceptors(client)
  return client
}
