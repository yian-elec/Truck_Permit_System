import { useNavigate } from 'react-router-dom'

import { appConfig } from '@/shared/config/app-config'
import { routePaths } from '@/shared/constants/route-paths'

import { RegisterForm } from '../components/RegisterForm'

export function RegisterPage() {
  const navigate = useNavigate()

  return (
    <div className="w-full max-w-sm space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">建立帳戶</h1>
        <p className="text-sm text-muted-foreground">註冊 {appConfig.appName}</p>
      </div>
      <RegisterForm onRegistered={() => navigate(routePaths.login, { replace: true })} />
    </div>
  )
}
