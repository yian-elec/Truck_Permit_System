import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'

import { useAuthStore } from '@/features/auth/store/auth.store'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const accessToken = useAuthStore((s) => s.accessToken)
  const location = useLocation()

  if (!accessToken) {
    return <Navigate to={routePaths.login} replace state={{ from: location }} />
  }

  return children
}

/** Only allow /mfa when an MFA challenge is pending (no access token yet). */
export function MfaRouteGuard({ children }: { children: ReactNode }) {
  const accessToken = useAuthStore((s) => s.accessToken)
  const mfaChallenge = useAuthStore((s) => s.mfaChallenge)

  if (accessToken) {
    return <Navigate to={routePaths.applicant} replace />
  }

  if (!mfaChallenge?.challenge_id) {
    return <Navigate to={routePaths.login} replace />
  }

  return children
}
