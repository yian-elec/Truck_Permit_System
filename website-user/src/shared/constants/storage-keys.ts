export const storageKeys = {
  /** Bearer access_token */
  accessToken: 'app.auth.access_token',
  theme: 'app.theme',
  /** JSON: pending MFA challenge (challenge_id, etc.) */
  mfaChallenge: 'app.auth.mfa_challenge',
} as const
