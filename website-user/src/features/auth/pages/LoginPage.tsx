import { appConfig } from '@/shared/config/app-config'

import { LoginForm } from '../components/LoginForm'

export function LoginPage() {
  return (
    <div className="w-full space-y-6">
      <div className="space-y-1.5">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">歡迎回來</h1>
        <p className="text-sm text-muted-foreground">登入 {appConfig.appName} 系統</p>
      </div>
      <LoginForm />
    </div>
  )
}
