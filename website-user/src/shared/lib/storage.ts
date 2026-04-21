import { logger } from './logger'

function guard(key: string): boolean {
  try {
    return typeof localStorage !== 'undefined'
  } catch {
    logger.warn('localStorage unavailable', key)
    return false
  }
}

export const storage = {
  get(key: string): string | null {
    if (!guard(key)) return null
    try {
      return localStorage.getItem(key)
    } catch {
      return null
    }
  },

  set(key: string, value: string): void {
    if (!guard(key)) return
    try {
      localStorage.setItem(key, value)
    } catch {
      logger.warn('Failed to write localStorage', key)
    }
  },

  remove(key: string): void {
    if (!guard(key)) return
    try {
      localStorage.removeItem(key)
    } catch {
      logger.warn('Failed to remove localStorage', key)
    }
  },
}
