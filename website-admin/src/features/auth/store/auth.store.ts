import { create } from 'zustand'

import { storageKeys } from '@/shared/constants/storage-keys'
import { storage } from '@/shared/lib/storage'

import type { AuthUser } from '../types/auth.types'

function readToken(): string | null {
  return storage.get(storageKeys.authToken)
}

function readSessionId(): string | null {
  return storage.get(storageKeys.authSessionId)
}

type AuthState = {
  token: string | null
  sessionId: string | null
  user: AuthUser | null
  setSession: (token: string, sessionId: string | null, user?: AuthUser | null) => void
  clearSession: () => void
  setUser: (user: AuthUser | null) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: readToken(),
  sessionId: readSessionId(),
  user: null,
  setSession: (token, sessionId, user = null) => {
    storage.set(storageKeys.authToken, token)
    if (sessionId) {
      storage.set(storageKeys.authSessionId, sessionId)
    } else {
      storage.remove(storageKeys.authSessionId)
    }
    set({ token, sessionId, user })
  },
  clearSession: () => {
    storage.remove(storageKeys.authToken)
    storage.remove(storageKeys.authSessionId)
    try {
      sessionStorage.removeItem(storageKeys.mfaChallengeId)
    } catch {
      /* ignore */
    }
    set({ token: null, sessionId: null, user: null })
  },
  setUser: (user) => set({ user }),
}))
