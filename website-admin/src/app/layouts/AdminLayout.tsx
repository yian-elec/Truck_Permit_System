import {
  ChevronLeft,
  ChevronRight,
  LogOut,
  Menu,
  Moon,
  Sun,
  LayoutDashboard,
  ClipboardList,
  ShieldAlert,
  Map,
  Terminal,
  UserCog,
  Truck,
} from 'lucide-react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { appConfig } from '@/shared/config/app-config'
import {
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

const navItems = [
  { to: routePaths.adminHome, label: '儀表板', icon: LayoutDashboard, end: true },
  { to: routePaths.reviewTasks, label: '待審任務', icon: ClipboardList, end: false },
  { to: routePaths.ruleList, label: '規則管理', icon: ShieldAlert, end: false },
  { to: routePaths.mapImports, label: '圖資管理', icon: Map, end: false },
  { to: routePaths.ops, label: '系統查詢', icon: Terminal, end: false },
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
    return [...crumbs, { label: '系統查詢' }]
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
      {/* Sidebar */}
      <aside
        className={cn(
          'sticky top-0 h-screen shrink-0 border-r border-border bg-sidebar flex flex-col transition-[width] duration-200',
          sidebarOpen ? 'w-56' : 'w-0 overflow-hidden md:w-14',
        )}
      >
        {/* Logo */}
        <div className={cn(
          'flex h-14 shrink-0 items-center gap-2 border-b border-sidebar-muted px-3',
          !sidebarOpen && 'justify-center px-2',
        )}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-active">
            <Truck className="h-4 w-4 text-sidebar-active-foreground" />
          </div>
          {sidebarOpen && (
            <span className="truncate text-sm font-semibold text-sidebar-foreground">
              {appConfig.appName}
            </span>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-0.5 overflow-y-auto p-2 py-3">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-active text-sidebar-active-foreground'
                    : 'text-sidebar-muted-foreground hover:bg-sidebar-muted hover:text-sidebar-foreground',
                  !sidebarOpen && 'justify-center px-2',
                )
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {sidebarOpen && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Bottom — 固定在底部 */}
        <div className="shrink-0 border-t border-sidebar-muted p-2 space-y-1">
          {/* 角色權限 */}
          {user?.id ? (
            <NavLink
              to={routePaths.userRoles(user.id)}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-active text-sidebar-active-foreground'
                    : 'text-sidebar-muted-foreground hover:bg-sidebar-muted hover:text-sidebar-foreground',
                  !sidebarOpen && 'justify-center px-2',
                )
              }
            >
              <UserCog className="h-4 w-4 shrink-0" />
              {sidebarOpen && <span>角色權限</span>}
            </NavLink>
          ) : null}

          {/* 帳號 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                type="button"
                className={cn(
                  'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-sidebar-muted',
                  !sidebarOpen && 'justify-center px-2',
                )}
              >
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sidebar-active text-xs font-semibold text-sidebar-active-foreground">
                  {user?.email?.[0]?.toUpperCase() ?? 'A'}
                </div>
                {sidebarOpen && (
                  <div className="min-w-0 text-left">
                    <p className="truncate text-xs font-medium text-sidebar-foreground">
                      {user?.displayName ?? user?.email ?? '帳戶'}
                    </p>
                  </div>
                )}
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent side="right" align="end">
              <DropdownMenuLabel>{user?.email ?? '已登入'}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setTheme('light')}>
                <Sun className="h-4 w-4" />淺色{theme === 'light' ? ' ✓' : ''}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('dark')}>
                <Moon className="h-4 w-4" />深色{theme === 'dark' ? ' ✓' : ''}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('system')}>
                系統預設{theme === 'system' ? ' ✓' : ''}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => logout.mutate()} disabled={logout.isPending}>
                <LogOut className="h-4 w-4" />登出
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* 收合按鈕 */}
          <button
            type="button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={cn(
              'hidden w-full items-center gap-3 rounded-lg px-3 py-2 text-xs text-sidebar-muted-foreground transition-colors hover:bg-sidebar-muted hover:text-sidebar-foreground md:flex',
              !sidebarOpen && 'justify-center px-2',
            )}
          >
            {sidebarOpen
              ? <><ChevronLeft className="h-4 w-4" /><span>收起</span></>
              : <ChevronRight className="h-4 w-4" />
            }
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top bar */}
        <header className="border-border bg-background/95 sticky top-0 z-40 flex h-14 shrink-0 items-center gap-3 border-b px-4 backdrop-blur">
          {/* Mobile toggle */}
          <button
            type="button"
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground md:hidden"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="開啟選單"
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Breadcrumb */}
          <div className="min-w-0 flex-1">
            <h1 className="truncate text-base font-semibold">{pageTitle}</h1>
            <nav className="text-muted-foreground flex flex-wrap items-center gap-1 text-xs">
              {crumbs.map((c, i) => (
                <span key={`${c.label}-${i}`} className="flex items-center gap-1">
                  {i > 0 ? <span className="text-muted-foreground/50">/</span> : null}
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
