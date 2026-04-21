import { z } from 'zod'

const envSchema = z
  .object({
    VITE_API_BASE_URL: z.string().optional(),
    VITE_APP_NAME: z.string().optional(),
    MODE: z.string(),
    DEV: z.boolean(),
    PROD: z.boolean(),
  })
  .superRefine((data, ctx) => {
    if (data.PROD) {
      const base = data.VITE_API_BASE_URL?.trim() ?? ''
      if (base.length === 0) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message:
            '正式環境必須設定 VITE_API_BASE_URL（後端 API 根位址，例如 https://api.example.com）',
          path: ['VITE_API_BASE_URL'],
        })
      }
    }
  })

const parsed = envSchema.safeParse({
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL as string | undefined,
  VITE_APP_NAME: import.meta.env.VITE_APP_NAME as string | undefined,
  MODE: import.meta.env.MODE,
  DEV: import.meta.env.DEV,
  PROD: import.meta.env.PROD,
})

if (!parsed.success) {
  console.error('Invalid environment variables', parsed.error.flatten())
  throw new Error('Invalid environment configuration')
}

export const env = parsed.data
