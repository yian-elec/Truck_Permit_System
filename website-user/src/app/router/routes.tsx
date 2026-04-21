import { Navigate, type RouteObject } from 'react-router-dom'

import { ApplicantLayout } from '@/app/layouts/ApplicantLayout'
import { AuthLayout } from '@/app/layouts/AuthLayout'
import { PublicLayout } from '@/app/layouts/PublicLayout'
import { ApplicantHomePage } from '@/features/applicant-home/pages/ApplicantHomePage'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { MfaVerifyPage } from '@/features/auth/pages/MfaVerifyPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { ApplicationDetailPage } from '@/features/application/pages/ApplicationDetailPage'
import { ApplicationEditorPage } from '@/features/application/pages/ApplicationEditorPage'
import { ApplicationListPage } from '@/features/application/pages/ApplicationListPage'
import { NewApplicationPage } from '@/features/application/pages/NewApplicationPage'
import { ConsentPage } from '@/features/public-service/pages/ConsentPage'
import { ServiceHomePage } from '@/features/public-service/pages/ServiceHomePage'
import { PermitPage } from '@/features/permit/pages/PermitPage'
import { SupplementPage } from '@/features/supplement/pages/SupplementPage'
import { routePaths } from '@/shared/constants/route-paths'

import { MfaRouteGuard, ProtectedRoute } from './guards'

export const appRoutes: RouteObject[] = [
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { index: true, element: <ServiceHomePage /> },
      { path: 'consent', element: <ConsentPage /> },
    ],
  },
  {
    path: routePaths.login,
    element: (
      <AuthLayout>
        <LoginPage />
      </AuthLayout>
    ),
  },
  {
    path: routePaths.register,
    element: (
      <AuthLayout>
        <RegisterPage />
      </AuthLayout>
    ),
  },
  {
    path: routePaths.mfa,
    element: (
      <AuthLayout>
        <MfaRouteGuard>
          <MfaVerifyPage />
        </MfaRouteGuard>
      </AuthLayout>
    ),
  },
  {
    path: routePaths.applicant,
    element: (
      <ProtectedRoute>
        <ApplicantLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <ApplicantHomePage /> },
      { path: 'applications', element: <ApplicationListPage /> },
      { path: 'applications/new', element: <NewApplicationPage /> },
      { path: 'applications/:applicationId', element: <ApplicationDetailPage /> },
      { path: 'applications/:applicationId/edit', element: <ApplicationEditorPage /> },
      { path: 'applications/:applicationId/supplement', element: <SupplementPage /> },
      { path: 'applications/:applicationId/permit', element: <PermitPage /> },
    ],
  },
  {
    path: '*',
    element: <Navigate to={routePaths.home} replace />,
  },
]
