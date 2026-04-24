import { z } from 'zod'

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().optional(),
  VITE_APP_NAME: z.string().optional(),
  MODE: z.string(),
  DEV: z.boolean(),
  PROD: z.boolean(),
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
