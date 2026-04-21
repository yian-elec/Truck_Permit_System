/// <reference types="vite/client" />
/// <reference types="vitest/globals" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_APP_NAME?: string
  /** 可選：覆寫 KML 匯入表單預設來源網址（未設定則用程式內建預設）。 */
  readonly VITE_DEFAULT_KML_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
