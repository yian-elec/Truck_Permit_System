import { env } from './env'

/**
 * 未設定 VITE_API_BASE_URL 時，開發模式預設連本機後端，否則前端會對 Vite 自己發 /api/... 而得到 404 Not Found。
 */
const apiBaseFromEnv = env.VITE_API_BASE_URL?.replace(/\/$/, '').trim() ?? ''

export const appConfig = {
  apiBaseUrl: apiBaseFromEnv || (env.DEV ? 'http://localhost:8000' : ''),
  appName: env.VITE_APP_NAME ?? 'App',
  isDev: env.DEV,
  mode: env.MODE,
} as const
