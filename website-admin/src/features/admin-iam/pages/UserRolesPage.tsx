import { useState } from 'react'
import { useParams } from 'react-router-dom'

import { SectionCard } from '@/shared/ui'
import { JsonPreview } from '@/shared/ui'

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
      <SectionCard title="使用者摘要" description="由目前登入者 /auth/me 對照路徑 userId">
        <p className="text-sm">
          路徑 userId：<span className="font-mono">{userId}</span>
        </p>
        {me.data ? (
          <p className="text-muted-foreground mt-2 text-sm">
            登入者：{me.data.displayName}（{me.data.email}）· id={me.data.id}
          </p>
        ) : null}
      </SectionCard>

      <SectionCard title="有效權限" description="GET /auth/me/permissions">
        {perm.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : (
          <JsonPreview value={perm.data ?? []} />
        )}
      </SectionCard>

      <SectionCard title="角色指派" description="以對話框送出 UC-IAM-04">
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
