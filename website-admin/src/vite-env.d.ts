/// <reference types="vite/client" />
/// <reference types="vitest/globals" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  /** 未設 `VITE_API_BASE_URL` 時，與 `window.location.hostname` 併用；預設 8000。 */
  readonly VITE_API_PORT?: string
  readonly VITE_APP_NAME?: string
  /** 可選：覆寫 KML 匯入表單預設來源網址（未設定則用程式內建預設）。 */
  readonly VITE_DEFAULT_KML_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
