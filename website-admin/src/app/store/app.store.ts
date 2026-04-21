import { create } from 'zustand'

import { storageKeys } from '@/shared/constants/storage-keys'
import { storage } from '@/shared/lib/storage'

export type ThemeMode = 'light' | 'dark' | 'system'

type AppState = {
  theme: ThemeMode
  sidebarOpen: boolean
  setTheme: (theme: ThemeMode) => void
  toggleSidebar: () => void
}

function readTheme(): ThemeMode {
  const raw = storage.get(storageKeys.theme)
  if (raw === 'light' || raw === 'dark' || raw === 'system') return raw
  return 'system'
}

export const useAppStore = create<AppState>((set, get) => ({
  theme: readTheme(),
  sidebarOpen: true,
  setTheme: (theme) => {
    storage.set(storageKeys.theme, theme)
    set({ theme })
  },
  toggleSidebar: () => set({ sidebarOpen: !get().sidebarOpen }),
}))
