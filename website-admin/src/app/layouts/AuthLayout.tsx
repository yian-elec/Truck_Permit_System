import { Navigate } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import type { WithChildren } from '@/shared/types/ui'

import { useAuthStore } from '@/features/auth/store/auth.store'

export function AuthLayout({ children }: WithChildren) {
  const token = useAuthStore((s) => s.token)

  if (token) {
    return <Navigate to={routePaths.home} replace />
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">{children}</div>
  )
}
