import { appConfig } from '@/shared/config/app-config'

import { LoginForm } from '../components/LoginForm'

export function LoginPage() {
  return (
    <div className="w-full max-w-sm space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">登入</h1>
        <p className="text-sm text-muted-foreground">登入 {appConfig.appName}</p>
      </div>
      <LoginForm />
    </div>
  )
}
