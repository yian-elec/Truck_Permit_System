import { z } from 'zod'

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().optional(),
  VITE_APP_NAME: z.string().optional(),
  VITE_GOOGLE_MAPS_API_KEY: z.string().optional(),
  /** 附件完成上傳回報時之儲存桶（須與後端 presign 設定一致） */
  VITE_ATTACHMENT_BUCKET_NAME: z.string().optional(),
  VITE_ATTACHMENT_STORAGE_PROVIDER: z.string().optional(),
  MODE: z.string(),
  DEV: z.boolean(),
})

const parsed = envSchema.safeParse({
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL as string | undefined,
  VITE_APP_NAME: import.meta.env.VITE_APP_NAME as string | undefined,
  VITE_GOOGLE_MAPS_API_KEY: import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined,
  VITE_ATTACHMENT_BUCKET_NAME: import.meta.env.VITE_ATTACHMENT_BUCKET_NAME as string | undefined,
  VITE_ATTACHMENT_STORAGE_PROVIDER: import.meta.env.VITE_ATTACHMENT_STORAGE_PROVIDER as string | undefined,
  MODE: import.meta.env.MODE,
  DEV: import.meta.env.DEV,
})

if (!parsed.success) {
  console.error('Invalid environment variables', parsed.error.flatten())
  throw new Error('Invalid environment configuration')
}

export const env = parsed.data

/**
 * 附件「完成上傳」API 所需之 bucket 名稱（須與後端建檔時預期一致）。
 * 開發環境若未設 `VITE_ATTACHMENT_BUCKET_NAME`，預設 `permit-dev`（與後端 e2e 相同）。
 */
export function getAttachmentBucketName(): string | null {
  const t = env.VITE_ATTACHMENT_BUCKET_NAME?.trim()
  if (t) return t
  if (env.DEV) return 'permit-dev'
  return null
}

/** 後端 noop 檔案埠之占位 presign URL（`storage.example.invalid`）；開發時略過直傳。 */
export function shouldSkipDirectUploadToStorage(uploadUrl: string): boolean {
  return env.DEV && uploadUrl.includes('storage.example.invalid')
}
