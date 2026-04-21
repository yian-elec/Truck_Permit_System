import type { MeResponse } from '../api/get-me'

export type AuthUser = MeResponse

export type MfaChallengeState = {
  challenge_id: string
  session_id?: string
}

export type LoginMode = 'password'
