import { appConfig } from '@/shared/config/app-config'

const prefix = '[app]'

export const logger = {
  debug: (...args: unknown[]) => {
    if (appConfig.isDev) console.debug(prefix, ...args)
  },
  info: (...args: unknown[]) => {
    if (appConfig.isDev) console.info(prefix, ...args)
  },
  warn: (...args: unknown[]) => {
    console.warn(prefix, ...args)
  },
  error: (...args: unknown[]) => {
    console.error(prefix, ...args)
  },
}
