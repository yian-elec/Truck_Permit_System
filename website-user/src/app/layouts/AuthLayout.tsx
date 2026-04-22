import { Navigate } from 'react-router-dom'
import { Truck } from 'lucide-react'

import { routePaths } from '@/shared/constants/route-paths'
import { appConfig } from '@/shared/config/app-config'
import type { WithChildren } from '@/shared/types/ui'

import { useAuthStore } from '@/features/auth/store/auth.store'

export function AuthLayout({ children }: WithChildren) {
  const accessToken = useAuthStore((s) => s.accessToken)

  if (accessToken) {
    return <Navigate to={routePaths.applicant} replace />
  }

  return (
    <div className="flex min-h-screen">
      {/* Left panel */}
      <div className="hidden w-1/2 flex-col justify-between bg-sidebar p-12 lg:flex">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sidebar-active">
            <Truck className="h-5 w-5 text-sidebar-active-foreground" />
          </div>
          <span className="text-base font-semibold text-sidebar-foreground">{appConfig.appName}</span>
        </div>
        <div className="space-y-4">
          <blockquote className="text-2xl font-semibold leading-relaxed text-sidebar-foreground">
            "線上申請大貨車臨時通行證，全程數位化，快速便利。"
          </blockquote>
          <p className="text-sidebar-muted-foreground">新北市政府警察局交通警察大隊</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-sidebar-muted-foreground">
          <span>安全加密</span>
          <span>·</span>
          <span>個資保護</span>
          <span>·</span>
          <span>24小時服務</span>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex flex-1 items-center justify-center bg-background p-6">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary">
              <Truck className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="text-sm font-semibold text-foreground">{appConfig.appName}</span>
          </div>
          {children}
        </div>
      </div>
    </div>
  )
}
