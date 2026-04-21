import { MfaVerifyForm } from '../components/MfaVerifyForm'

export function MfaVerifyPage() {
  return (
    <div className="w-full max-w-sm space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">驗證登入</h1>
        <p className="text-sm text-muted-foreground">需要完成多因素驗證。</p>
      </div>
      <MfaVerifyForm />
    </div>
  )
}
