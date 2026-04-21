import { env } from './env'

/**
 * Resolves API base URL: env override, else `http://{hostname}:8000` in browser.
 */
export function getApiBaseUrl(): string {
  const fromEnv = env.VITE_API_BASE_URL?.replace(/\/$/, '')
  if (fromEnv) return fromEnv

  if (typeof window !== 'undefined' && window.location?.hostname) {
    return `http://${window.location.hostname}:8000`
  }

  return ''
}
