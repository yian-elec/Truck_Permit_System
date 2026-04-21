import { Link, Outlet } from 'react-router-dom'

import { appConfig } from '@/shared/config/app-config'
import { routePaths } from '@/shared/constants/route-paths'
import { Button } from '@/shared/ui'

import { useAuthStore } from '@/features/auth/store/auth.store'

export function PublicLayout() {
  const accessToken = useAuthStore((s) => s.accessToken)

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-border bg-background">
        <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link className="text-sm font-semibold" to={routePaths.home}>
            {appConfig.appName}
          </Link>
          <nav className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to={routePaths.consent}>條款</Link>
            </Button>
            {accessToken ? (
              <Button size="sm" asChild>
                <Link to={routePaths.applicant}>我的帳戶</Link>
              </Button>
            ) : (
              <>
                <Button variant="outline" size="sm" asChild>
                  <Link to={routePaths.login}>登入</Link>
                </Button>
                <Button size="sm" asChild>
                  <Link to={routePaths.register}>註冊</Link>
                </Button>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
