import { Navigate, type RouteObject } from 'react-router-dom'

import { AdminDashboardPage } from '@/features/admin-dashboard/pages/AdminDashboardPage'
import { MapImportPage } from '@/features/admin-map-import/pages/MapImportPage'
import { AuditLogPage } from '@/features/admin-work/pages/AuditLogPage'
import { WorkCenterPage } from '@/features/admin-work/pages/WorkCenterPage'
import { RuleDetailPage } from '@/features/admin-restriction/pages/RuleDetailPage'
import { RuleListPage } from '@/features/admin-restriction/pages/RuleListPage'
import { UserRolesPage } from '@/features/admin-iam/pages/UserRolesPage'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { MfaPage } from '@/features/auth/pages/MfaPage'
import { ReviewCasePage } from '@/features/review-case/pages/ReviewCasePage'
import { ReviewRoutePage } from '@/features/review-routing/pages/ReviewRoutePage'
import { routePaths, workCenterUrl } from '@/shared/constants/route-paths'

import { AdminLayout } from '../layouts/AdminLayout'
import { AppLayout } from '../layouts/AppLayout'
import { AuthLayout } from '../layouts/AuthLayout'
import { AdminRoute, ProtectedRoute } from './guards'

export const appRoutes: RouteObject[] = [
  {
    path: '/login',
    element: (
      <AuthLayout>
        <LoginPage />
      </AuthLayout>
    ),
  },
  {
    path: '/mfa',
    element: (
      <AuthLayout>
        <MfaPage />
      </AuthLayout>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [{ index: true, element: <Navigate to={routePaths.adminHome} replace /> }],
  },
  {
    path: '/admin',
    element: (
      <AdminRoute>
        <AdminLayout />
      </AdminRoute>
    ),
    children: [
      { index: true, element: <AdminDashboardPage /> },
      { path: 'work', element: <WorkCenterPage /> },
      { path: 'audit-log', element: <AuditLogPage /> },
      { path: 'review/tasks', element: <Navigate to={workCenterUrl('review')} replace /> },
      { path: 'review/applications/:applicationId', element: <ReviewCasePage /> },
      { path: 'review/applications/:applicationId/route', element: <ReviewRoutePage /> },
      { path: 'restrictions/rules', element: <RuleListPage /> },
      { path: 'restrictions/rules/:ruleId', element: <RuleDetailPage /> },
      { path: 'map-imports', element: <MapImportPage /> },
      { path: 'ops', element: <Navigate to={workCenterUrl('ocr')} replace /> },
      { path: 'users/:userId/roles', element: <UserRolesPage /> },
    ],
  },
  {
    path: '*',
    element: <Navigate to={routePaths.adminHome} replace />,
  },
]
