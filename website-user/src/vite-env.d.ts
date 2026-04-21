/// <reference types="vite/client" />
/// <reference types="vitest/globals" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_APP_NAME?: string
  readonly VITE_GOOGLE_MAPS_API_KEY?: string
  readonly VITE_ATTACHMENT_BUCKET_NAME?: string
  readonly VITE_ATTACHMENT_STORAGE_PROVIDER?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
