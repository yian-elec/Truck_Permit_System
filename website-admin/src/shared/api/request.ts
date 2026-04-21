import type { AxiosResponse } from 'axios'

import { apiClient } from './client'
import type { RequestConfig } from './types'

export async function get<T>(url: string, config?: RequestConfig): Promise<AxiosResponse<T>> {
  return apiClient.get<T>(url, config)
}

export async function post<T, B = unknown>(
  url: string,
  body?: B,
  config?: RequestConfig,
): Promise<AxiosResponse<T>> {
  return apiClient.post<T>(url, body, config)
}

export async function put<T, B = unknown>(
  url: string,
  body?: B,
  config?: RequestConfig,
): Promise<AxiosResponse<T>> {
  return apiClient.put<T>(url, body, config)
}

export async function patch<T, B = unknown>(
  url: string,
  body?: B,
  config?: RequestConfig,
): Promise<AxiosResponse<T>> {
  return apiClient.patch<T>(url, body, config)
}

export async function del<T>(url: string, config?: RequestConfig): Promise<AxiosResponse<T>> {
  return apiClient.delete<T>(url, config)
}
