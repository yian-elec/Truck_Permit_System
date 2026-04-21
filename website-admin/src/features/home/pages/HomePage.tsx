import { appConfig } from '@/shared/config/app-config'
import { PageContainer } from '@/shared/ui'

import { useAuthStore } from '@/features/auth/store/auth.store'

export function HomePage() {
  const user = useAuthStore((s) => s.user)

  return (
    <PageContainer as="main">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Home</h1>
        <p className="text-muted-foreground">
          Welcome to {appConfig.appName}
          {user?.email ? `, ${user.email}` : ''}.
        </p>
      </div>
    </PageContainer>
  )
}
