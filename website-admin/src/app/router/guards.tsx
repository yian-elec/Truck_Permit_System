import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'

import { useAuthStore } from '@/features/auth/store/auth.store'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const token = useAuthStore((s) => s.token)
  const location = useLocation()

  if (!token) {
    return <Navigate to={routePaths.login} replace state={{ from: location }} />
  }

  return children
}

/** 管理區：需已登入；權限清單由版面或頁面按需載入。 */
export function AdminRoute({ children }: { children: ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>
}
