import type { ReactNode } from 'react'
import { useEffect } from 'react'

import { useMediaQuery } from '@/shared/hooks/useMediaQuery'

import { useAppStore, type ThemeMode } from '../store/app.store'

function resolveTheme(mode: ThemeMode, prefersDark: boolean): 'light' | 'dark' {
  if (mode === 'system') return prefersDark ? 'dark' : 'light'
  return mode
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const theme = useAppStore((s) => s.theme)
  const prefersDark = useMediaQuery('(prefers-color-scheme: dark)')

  useEffect(() => {
    const resolved = resolveTheme(theme, prefersDark)
    document.documentElement.classList.toggle('dark', resolved === 'dark')
  }, [theme, prefersDark])

  return children
}
