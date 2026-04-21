import { create } from 'zustand'

import { storageKeys } from '@/shared/constants/storage-keys'
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from '@/shared/lib/auth-token'
import { storage } from '@/shared/lib/storage'

import type { AuthUser, MfaChallengeState } from '../types/auth.types'

function readMfaChallenge(): MfaChallengeState | null {
  try {
    const raw = storage.get(storageKeys.mfaChallenge)
    if (!raw) return null
    return JSON.parse(raw) as MfaChallengeState
  } catch {
    return null
  }
}

function writeMfaChallenge(challenge: MfaChallengeState | null) {
  if (!challenge) {
    storage.remove(storageKeys.mfaChallenge)
    return
  }
  storage.set(storageKeys.mfaChallenge, JSON.stringify(challenge))
}

type AuthState = {
  accessToken: string | null
  user: AuthUser | null
  mfaChallenge: MfaChallengeState | null
  setSession: (accessToken: string, user?: AuthUser | null) => void
  clearSession: () => void
  setUser: (user: AuthUser | null) => void
  setMfaChallenge: (challenge: MfaChallengeState | null) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: getAccessToken(),
  user: null,
  mfaChallenge: readMfaChallenge(),
  setSession: (accessToken, user = null) => {
    setAccessToken(accessToken)
    writeMfaChallenge(null)
    set({ accessToken, user, mfaChallenge: null })
  },
  clearSession: () => {
    clearAccessToken()
    writeMfaChallenge(null)
    set({ accessToken: null, user: null, mfaChallenge: null })
  },
  setUser: (user) => set({ user }),
  setMfaChallenge: (challenge) => {
    writeMfaChallenge(challenge)
    set({ mfaChallenge: challenge })
  },
}))

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken())
}
