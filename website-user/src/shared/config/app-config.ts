import { getApiBaseUrl } from './get-api-base-url'
import { env } from './env'

export const appConfig = {
  get apiBaseUrl() {
    return getApiBaseUrl()
  },
  appName: env.VITE_APP_NAME ?? '重型貨車通行證',
  googleMapsApiKey: env.VITE_GOOGLE_MAPS_API_KEY ?? '',
  isDev: env.DEV,
  mode: env.MODE,
} as const
