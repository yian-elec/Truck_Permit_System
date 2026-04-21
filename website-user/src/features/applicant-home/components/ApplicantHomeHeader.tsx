import { useAuthStore } from '@/features/auth/store/auth.store'

export function ApplicantHomeHeader() {
  const user = useAuthStore((s) => s.user)

  return (
    <div className="space-y-1">
      <h1 className="text-2xl font-semibold tracking-tight">申請首頁</h1>
      <p className="text-muted-foreground">
        您好{user?.display_name ? `，${user.display_name}` : ''}，在此管理您的通行證申請。
      </p>
    </div>
  )
}
