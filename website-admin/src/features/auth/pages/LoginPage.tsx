import { LoginForm } from '../components/LoginForm'

export function LoginPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">登入</h1>
        <p className="text-sm text-muted-foreground">請輸入帳號與密碼以繼續。</p>
      </div>
      <LoginForm />
    </div>
  )
}
