import { ChevronLeft, LogOut, Menu, Moon, Sun } from 'lucide-react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { appConfig } from '@/shared/config/app-config'
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui'
import { routePaths } from '@/shared/constants/route-paths'
import { cn } from '@/shared/lib/cn'

import { useLogout } from '@/features/auth/hooks/useLogout'
import { useMe } from '@/features/auth/hooks/useMe'
import { usePermissions } from '@/features/auth/hooks/usePermissions'
import { useAuthStore } from '@/features/auth/store/auth.store'

import { useAppStore } from '../store/app.store'
import { useUiStore } from '../store/ui.store'

const navItems: { to: string; label: string }[] = [
  { to: routePaths.adminHome, label: 'Dashboard' },
  { to: routePaths.reviewTasks, label: '待審任務' },
  { to: routePaths.ruleList, label: '規則管理' },
  { to: routePaths.mapImports, label: '圖資管理' },
  { to: routePaths.ops, label: 'Ops 查詢' },
]

function breadcrumbFromPath(pathname: string): { label: string; to?: string }[] {
  const crumbs: { label: string; to?: string }[] = [{ label: '管理後台', to: routePaths.adminHome }]
  if (pathname === routePaths.adminHome) return crumbs
  if (pathname.startsWith('/admin/review/tasks')) {
    return [...crumbs, { label: '待審任務' }]
  }
  if (pathname.includes('/admin/review/applications/') && pathname.endsWith('/route')) {
    return [...crumbs, { label: '待審任務', to: routePaths.reviewTasks }, { label: '路線審查' }]
  }
  if (pathname.includes('/admin/review/applications/')) {
    return [...crumbs, { label: '待審任務', to: routePaths.reviewTasks }, { label: '單案審核' }]
  }
  if (pathname.startsWith('/admin/restrictions/rules')) {
    const parts = [...crumbs, { label: '規則管理', to: routePaths.ruleList }]
    const segs = pathname.split('/').filter(Boolean)
    const ruleId = segs[segs.length - 1]
    if (segs.length > 3 && ruleId && ruleId !== 'rules') {
      parts.push({ label: `規則 ${ruleId.slice(0, 8)}…` })
    }
    return parts
  }
  if (pathname.startsWith(routePaths.mapImports)) {
    return [...crumbs, { label: '圖資管理' }]
  }
  if (pathname.startsWith(routePaths.ops)) {
    return [...crumbs, { label: 'Ops 查詢' }]
  }
  if (pathname.includes('/admin/users/') && pathname.endsWith('/roles')) {
    return [...crumbs, { label: '角色權限' }]
  }
  return [...crumbs, { label: pathname }]
}

export function AdminLayout() {
  useMe()
  usePermissions()
  const user = useAuthStore((s) => s.user)
  const theme = useAppStore((s) => s.theme)
  const setTheme = useAppStore((s) => s.setTheme)
  const logout = useLogout()
  const location = useLocation()
  const sidebarOpen = useUiStore((s) => s.sidebarOpen)
  const setSidebarOpen = useUiStore((s) => s.setSidebarOpen)
  const globalLoading = useUiStore((s) => s.globalLoading)

  const crumbs = breadcrumbFromPath(location.pathname)
  const pageTitle = crumbs[crumbs.length - 1]?.label ?? appConfig.appName

  return (
    <div className="flex min-h-screen bg-background">
      <aside
        className={cn(
          'border-border bg-card/30 flex shrink-0 flex-col border-r transition-[width]',
          sidebarOpen ? 'w-56' : 'w-0 overflow-hidden md:w-14',
        )}
      >
        <div className="flex h-14 items-center gap-2 border-b border-border px-3">
          <span className="truncate text-sm font-semibold">{appConfig.appName}</span>
        </div>
        <nav className="flex flex-1 flex-col gap-0.5 p-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === routePaths.adminHome}
              className={({ isActive }) =>
                cn(
                  'rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
          <div className="mt-auto border-t border-border pt-2">
            {user?.id ? (
              <NavLink
                to={routePaths.userRoles(user.id)}
                className={({ isActive }) =>
                  cn(
                    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  )
                }
              >
                角色權限
              </NavLink>
            ) : (
              <span className="text-muted-foreground px-3 py-2 text-sm">角色權限</span>
            )}
          </div>
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-border bg-background/95 sticky top-0 z-40 flex h-14 shrink-0 items-center gap-3 border-b px-4 backdrop-blur">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="hidden md:inline-flex"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar width"
          >
            <ChevronLeft
              className={cn('h-5 w-5 transition-transform', !sidebarOpen && 'rotate-180')}
            />
          </Button>
          <div className="min-w-0 flex-1">
            <h1 className="truncate text-base font-semibold">{pageTitle}</h1>
            <nav className="text-muted-foreground flex flex-wrap items-center gap-1 text-xs">
              {crumbs.map((c, i) => (
                <span key={`${c.label}-${i}`} className="flex items-center gap-1">
                  {i > 0 ? <span className="text-muted-foreground/70">/</span> : null}
                  {c.to ? (
                    <NavLink to={c.to} className="hover:text-foreground underline-offset-2 hover:underline">
                      {c.label}
                    </NavLink>
                  ) : (
                    <span>{c.label}</span>
                  )}
                </span>
              ))}
            </nav>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                Theme
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Appearance</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setTheme('light')}>
                <Sun className="h-4 w-4" />
                Light
                {theme === 'light' ? ' ✓' : ''}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('dark')}>
                <Moon className="h-4 w-4" />
                Dark
                {theme === 'dark' ? ' ✓' : ''}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('system')}>System</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="secondary" size="sm">
                {user?.displayName ?? user?.email ?? 'Account'}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>{user?.email ?? 'Signed in'}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => logout.mutate()} disabled={logout.isPending}>
                <LogOut className="h-4 w-4" />
                登出
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        <main className="relative flex-1">
          <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
            <Outlet />
          </div>
          {globalLoading ? (
            <div className="bg-background/60 fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm">
              <div className="border-border bg-card text-muted-foreground rounded-lg border px-4 py-3 text-sm shadow-lg">
                載入中…
              </div>
            </div>
          ) : null}
        </main>
      </div>
    </div>
  )
}
