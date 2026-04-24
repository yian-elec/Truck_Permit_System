import { useState } from 'react'
import { useParams } from 'react-router-dom'

import { SectionCard } from '@/shared/ui'
import { formatPermissionLabel } from '@/shared/utils/admin-operator-copy'

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
      <p className="text-muted-foreground text-sm">此頁以管理者設定帳號可執行的工作為主。</p>

      <SectionCard title="帳號">
        <p className="text-sm text-foreground">
          {me.data?.displayName ? (
            <span>
              使用者 <span className="font-medium">{me.data.displayName}</span>（{me.data.email}）
            </span>
          ) : (
            <span>帳號識別碼（系統內用）：<span className="font-mono text-xs text-muted-foreground">{userId}</span></span>
          )}
        </p>
        {me.data ? (
          <p className="text-muted-foreground mt-2 text-xs">
            內部識別碼：<span className="font-mono">{userId}</span>
          </p>
        ) : null}
      </SectionCard>

      <SectionCard title="目前擁有權限（說明）">
        {perm.isLoading ? (
          <p className="text-muted-foreground text-sm">載入中…</p>
        ) : (
          <ul className="space-y-1.5">
            {(perm.data ?? []).map((p: string, i: number) => (
              <li key={i} className="rounded-md bg-muted px-3 py-2 text-sm text-foreground">
                {formatPermissionLabel(p)}
              </li>
            ))}
          </ul>
        )}
      </SectionCard>

      <SectionCard title="角色">
        <button
          type="button"
          className="text-primary text-sm font-medium underline"
          onClick={() => setOpen(true)}
        >
          指派或變更角色
        </button>
        <AssignRoleDialog userId={userId} open={open} onOpenChange={setOpen} />
      </SectionCard>
    </div>
  )
}
