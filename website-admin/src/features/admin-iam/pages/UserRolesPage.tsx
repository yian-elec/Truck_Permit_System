import { useState } from 'react'
import { useParams } from 'react-router-dom'

import { SectionCard } from '@/shared/ui'

import { usePermissions } from '@/features/auth/hooks/usePermissions'
import { useMe } from '@/features/auth/hooks/useMe'

import { AssignRoleDialog } from '../components/AssignRoleDialog'

export function UserRolesPage() {
  const { userId = '' } = useParams<{ userId: string }>()
  const me = useMe()
  const perm = usePermissions()
  const [open, setOpen] = useState(false)

  return (
    <div className="space-y-6">
      <SectionCard title="使用者摘要" >
        <p className="text-sm">
          使用者 ID：<span className="font-mono text-xs">{userId}</span>
        </p>
        {me.data ? (
          <p className="text-muted-foreground mt-2 text-sm">
            登入者：{me.data.displayName}（{me.data.email}）
          </p>
        ) : null}
      </SectionCard>

      <SectionCard title="有效權限" >
        {perm.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : (
          <ul className="space-y-1">
            {(perm.data ?? []).map((p: string, i: number) => (
              <li key={i} className="rounded-md bg-muted px-3 py-1.5 text-xs font-mono text-foreground">{p}</li>
            ))}
          </ul>
        )}
      </SectionCard>

      <SectionCard title="角色指派" >
        <button
          type="button"
          className="text-primary text-sm font-medium underline"
          onClick={() => setOpen(true)}
        >
          開啟指派角色
        </button>
        <AssignRoleDialog userId={userId} open={open} onOpenChange={setOpen} />
      </SectionCard>
    </div>
  )
}
