import { useCallback, useEffect, useState } from 'react'

import { logger } from '@/shared/lib/logger'

export function useLocalStorage<T>(key: string, initialValue: T) {
  const read = useCallback((): T => {
    try {
      const raw = localStorage.getItem(key)
      if (raw == null) return initialValue
      return JSON.parse(raw) as T
    } catch {
      logger.warn('useLocalStorage read failed', key)
      return initialValue
    }
  }, [key, initialValue])

  const [value, setValue] = useState<T>(read)

  useEffect(() => {
    setValue(read())
  }, [read])

  const setStored = useCallback(
    (next: T | ((prev: T) => T)) => {
      setValue((prev) => {
        const resolved = typeof next === 'function' ? (next as (p: T) => T)(prev) : next
        try {
          localStorage.setItem(key, JSON.stringify(resolved))
        } catch {
          logger.warn('useLocalStorage write failed', key)
        }
        return resolved
      })
    },
    [key],
  )

  const remove = useCallback(() => {
    try {
      localStorage.removeItem(key)
    } catch {
      logger.warn('useLocalStorage remove failed', key)
    }
    setValue(initialValue)
  }, [key, initialValue])

  return [value, setStored, remove] as const
}
