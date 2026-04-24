import { env } from './env'

/**
 * 後端 API 基底。與 admin 邏輯一致：優先 `VITE_API_BASE_URL`；未設時在瀏覽器內以 `window.location.hostname` 推斷同主機之 API（`VITE_API_PORT` 未設則 8000）。
 * 前後分離、不同網域、HTTPS 時請設定 `VITE_API_BASE_URL`；https 前頁 + 僅 http API 需代理或明確的 https API 位址。
 */
export function getApiBaseUrl(): string {
  const fromEnv = env.VITE_API_BASE_URL?.replace(/\/$/, '')?.trim() ?? ''
  if (fromEnv) return fromEnv

  const port = (import.meta.env.VITE_API_PORT as string | undefined)?.trim() || '8000'

  if (typeof window !== 'undefined' && window.location?.hostname) {
    return `http://${window.location.hostname}:${port}`
  }

  return ''
}
