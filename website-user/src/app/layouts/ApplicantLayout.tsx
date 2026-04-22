import { useState } from 'react'
import { LogOut, Moon, Sun } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

import { appConfig } from '@/shared/config/app-config'
import { routePaths } from '@/shared/constants/route-paths'
import { cn } from '@/shared/lib/cn'
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui'

import { useLogout } from '@/features/auth/hooks/useLogout'
import { useMe } from '@/features/auth/hooks/useMe'
import { useAuthStore } from '@/features/auth/store/auth.store'
import { CaseDescriptionDialog } from '@/features/public-service/components/CaseDescriptionDialog'
import { FormDownloadDialog } from '@/features/public-service/components/FormDownloadDialog'

import { useAppStore } from '../store/app.store'

const navClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
    isActive ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/80 hover:text-foreground',
  )

export function ApplicantLayout() {
  useMe()
  const user = useAuthStore((s) => s.user)
  const theme = useAppStore((s) => s.theme)
  const setTheme = useAppStore((s) => s.setTheme)
  const logout = useLogout()
  const [caseOpen, setCaseOpen] = useState(false)
  const [formOpen, setFormOpen] = useState(false)

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-border bg-background">
        <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-6">
            <NavLink className="shrink-0 text-sm font-semibold" to={routePaths.applicant}>
              {appConfig.appName}
            </NavLink>
            <nav className="hidden items-center gap-1 sm:flex">
              <NavLink className={navClass} to={routePaths.applicant} end>
                我的案件
              </NavLink>
              <NavLink className={navClass} to={routePaths.applicantApplicationNew}>
                建立新案件
              </NavLink>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-8 rounded-md"
                onClick={() => setCaseOpen(true)}
              >
                案件說明
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-8 rounded-md"
                onClick={() => setFormOpen(true)}
              >
                書表下載
              </Button>
            </nav>
          </div>
          <div className="flex shrink-0 items-center gap-1 sm:gap-2">
            <div className="flex items-center gap-1 sm:hidden">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setCaseOpen(true)}
              >
                案件
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setFormOpen(true)}
              >
                書表
              </Button>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  外觀
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>顯示設定</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setTheme('light')}>
                  <Sun className="h-4 w-4" />
                  淺色
                  {theme === 'light' ? ' ✓' : ''}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme('dark')}>
                  <Moon className="h-4 w-4" />
                  深色
                  {theme === 'dark' ? ' ✓' : ''}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme('system')}>跟隨系統</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="secondary" size="sm">
                  {user?.email ?? '帳戶'}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{user?.email ?? '已登入'}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => logout.mutate()}
                  disabled={logout.isPending}
                >
                  <LogOut className="h-4 w-4" />
                  登出
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>
      <CaseDescriptionDialog open={caseOpen} onOpenChange={setCaseOpen} />
      <FormDownloadDialog open={formOpen} onOpenChange={setFormOpen} />
      <Outlet />
    </div>
  )
}
