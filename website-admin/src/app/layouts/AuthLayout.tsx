import { Navigate } from 'react-router-dom'
import { Truck } from 'lucide-react'

import { routePaths } from '@/shared/constants/route-paths'
import type { WithChildren } from '@/shared/types/ui'
import { appConfig } from '@/shared/config/app-config'
import { useAuthStore } from '@/features/auth/store/auth.store'

export function AuthLayout({ children }: WithChildren) {
  const token = useAuthStore((s) => s.token)

  if (token) {
    return <Navigate to={routePaths.home} replace />
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* 左側品牌欄 — 桌面版才顯示 */}
      <div className="hidden lg:flex lg:w-[420px] lg:shrink-0 lg:flex-col lg:justify-between bg-sidebar p-10">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sidebar-active">
            <Truck className="h-5 w-5 text-sidebar-active-foreground" />
          </div>
          <span className="text-sm font-semibold text-sidebar-foreground">{appConfig.appName}</span>
        </div>
        <div className="space-y-2">
          <p className="text-xl font-semibold text-sidebar-foreground leading-snug">
            大型車輛通行許可<br />管理後台
          </p>
          <p className="text-sm text-sidebar-muted-foreground">
            供內部承辦人員審核申請、管理路網規則與查詢作業紀錄。
          </p>
        </div>
        <p className="text-xs text-sidebar-muted-foreground">© {new Date().getFullYear()} 道路管理系統</p>
      </div>

      {/* 右側登入區 */}
      <div className="flex flex-1 flex-col items-center justify-center p-6 sm:p-10">
        {/* 手機版 logo */}
        <div className="mb-8 flex items-center gap-2 lg:hidden">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Truck className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="text-sm font-semibold">{appConfig.appName}</span>
        </div>
        <div className="w-full max-w-sm">
          {children}
        </div>
      </div>
    </div>
  )
}
