import { env } from './env'

/**
 * 後端 API 基底網址（不含尾隨 `/`）。
 *
 * 1. **優先** `VITE_API_BASE_URL`：前後分離、不同網域、HTTPS、或 API 與本頁面不同主機時**務必**設定（建置前寫入 `.env.production`）。
 * 2. 未設定且在**瀏覽器**內執行：用 `window.location.hostname` + `VITE_API_PORT`（未設則 `8000`），即與你開啟網頁的「同一主機 + 通訊埠」相連；適合區網/外網用 **http://IP:前端埠** 開頁、後端在 **同 IP:8000** 的情境。
 * 3. 若前頁為 **https** 而 API 僅有 **http**，瀏覽器會擋（mixed content），此時需反向代理、或把 `VITE_API_BASE_URL` 設成 **https** 的 API 網址。
 */
export function getApiBaseUrl(): string {
  const fromEnv = env.VITE_API_BASE_URL?.replace(/\/$/, '').trim() ?? ''
  if (fromEnv) return fromEnv

  const port = (import.meta.env.VITE_API_PORT as string | undefined)?.trim() || '8000'

  if (typeof window !== 'undefined' && window.location?.hostname) {
    return `http://${window.location.hostname}:${port}`
  }
  if (env.DEV) {
    return `http://localhost:${port}`
  }
  return ''
}
