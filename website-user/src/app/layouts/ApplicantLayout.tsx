import { useState } from 'react'
import {
  LogOut,
  Moon,
  Sun,
  PlusCircle,
  Home,
  Download,
  Info,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Truck,
} from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

import { appConfig } from '@/shared/config/app-config'
import { routePaths } from '@/shared/constants/route-paths'
import { cn } from '@/shared/lib/cn'
import {
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

const navItems = [
  { icon: Home, label: '我的案件', to: routePaths.applicant, end: true },
  { icon: PlusCircle, label: '建立新案件', to: routePaths.applicantApplicationNew, end: false },
]

export function ApplicantLayout() {
  useMe()
  const user = useAuthStore((s) => s.user)
  const theme = useAppStore((s) => s.theme)
  const setTheme = useAppStore((s) => s.setTheme)
  const logout = useLogout()
  const [caseOpen, setCaseOpen] = useState(false)
  const [formOpen, setFormOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const sidebarContent = (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Logo */}
      <div
        className={cn(
          'flex shrink-0 items-center gap-3 border-b border-sidebar-muted px-4 py-4',
          collapsed && 'justify-center px-2',
        )}
      >
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-active">
          <Truck className="h-5 w-5 text-sidebar-active-foreground" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-sidebar-foreground">
              {appConfig.appName}
            </p>
            <p className="truncate text-xs text-sidebar-muted-foreground">申請人入口</p>
          </div>
        )}
      </div>

      {/* Nav — scrollable if needed */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-2 py-4">
        {navItems.map(({ icon: Icon, label, to, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-active text-sidebar-active-foreground'
                  : 'text-sidebar-muted-foreground hover:bg-sidebar-muted hover:text-sidebar-foreground',
                collapsed && 'justify-center px-2',
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}

        <div className="pt-2">
          {!collapsed && (
            <p className="mb-1 px-3 text-xs font-medium uppercase tracking-wider text-sidebar-muted-foreground">
              服務
            </p>
          )}
          <button
            type="button"
            onClick={() => { setCaseOpen(true); setMobileOpen(false) }}
            className={cn(
              'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-muted-foreground transition-colors hover:bg-sidebar-muted hover:text-sidebar-foreground',
              collapsed && 'justify-center px-2',
            )}
          >
            <Info className="h-4 w-4 shrink-0" />
            {!collapsed && <span>案件說明</span>}
          </button>
          <button
            type="button"
            onClick={() => { setFormOpen(true); setMobileOpen(false) }}
            className={cn(
              'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-muted-foreground transition-colors hover:bg-sidebar-muted hover:text-sidebar-foreground',
              collapsed && 'justify-center px-2',
            )}
          >
            <Download className="h-4 w-4 shrink-0" />
            {!collapsed && <span>書表下載</span>}
          </button>
        </div>
      </nav>

      {/* Bottom — 固定在底部，永遠可見 */}
      <div className="shrink-0 border-t border-sidebar-muted p-2 space-y-1">
        {/* User */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              className={cn(
                'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-sidebar-muted',
                collapsed && 'justify-center px-2',
              )}
            >
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sidebar-active text-xs font-semibold text-sidebar-active-foreground">
                {user?.email?.[0]?.toUpperCase() ?? 'U'}
              </div>
              {!collapsed && (
                <div className="min-w-0 text-left">
                  <p className="truncate text-xs font-medium text-sidebar-foreground">
                    {user?.email ?? '帳戶'}
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
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => logout.mutate()} disabled={logout.isPending}>
              <LogOut className="h-4 w-4" />登出
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Collapse toggle (desktop only) */}
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          className={cn(
            'hidden w-full items-center gap-3 rounded-lg px-3 py-2 text-xs text-sidebar-muted-foreground transition-colors hover:bg-sidebar-muted hover:text-sidebar-foreground lg:flex',
            collapsed && 'justify-center px-2',
          )}
        >
          {collapsed
            ? <ChevronRight className="h-4 w-4" />
            : <><ChevronLeft className="h-4 w-4" /><span>收起</span></>
          }
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'hidden lg:flex flex-col border-r border-border bg-sidebar transition-all duration-200',
          collapsed ? 'w-16' : 'w-60',
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setMobileOpen(false)}>
          <div className="absolute inset-0 bg-black/50" />
        </div>
      )}

      {/* Mobile Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 flex flex-col border-r border-border bg-sidebar transition-transform duration-200 lg:hidden',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex shrink-0 items-center justify-between border-b border-sidebar-muted px-4 py-4">
          <div className="flex items-center gap-2">
            <Truck className="h-5 w-5 text-sidebar-active-foreground" />
            <span className="text-sm font-semibold text-sidebar-foreground">{appConfig.appName}</span>
          </div>
          <button type="button" onClick={() => setMobileOpen(false)} className="text-sidebar-muted-foreground">
            <X className="h-5 w-5" />
          </button>
        </div>
        {sidebarContent}
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Mobile top bar */}
        <header className="flex items-center gap-3 border-b border-border bg-background px-4 py-3 lg:hidden">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="text-muted-foreground hover:text-foreground"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <Truck className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold">{appConfig.appName}</span>
          </div>
        </header>

        <main className="flex-1">
          <Outlet />
        </main>
      </div>

      <CaseDescriptionDialog open={caseOpen} onOpenChange={setCaseOpen} />
      <FormDownloadDialog open={formOpen} onOpenChange={setFormOpen} />
    </div>
  )
}
