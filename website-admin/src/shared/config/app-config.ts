import { env } from './env'

export const appConfig = {
  appName: env.VITE_APP_NAME ?? 'App',
  isDev: env.DEV,
  mode: env.MODE,
} as const
