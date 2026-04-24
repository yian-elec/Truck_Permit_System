import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { getRoleSelectOptions } from '@/shared/utils/admin-operator-copy'
import { Button, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, Input } from '@/shared/ui'

import { assignRole } from '../api/admin-iam-api'

type Props = {
  userId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

const selectClassName =
  'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50'

export function AssignRoleDialog({ userId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [roleCode, setRoleCode] = useState('')
  const [assignmentId, setAssignmentId] = useState<string>(() => crypto.randomUUID())
  const [scopeType, setScopeType] = useState('')
  const [scopeId, setScopeId] = useState('')

  const mutation = useMutation({
    mutationFn: () =>
      assignRole(userId, {
        role_code: roleCode,
        assignment_id: assignmentId,
        scope_type: scopeType || null,
        scope_id: scopeId || null,
      }),
    onSuccess: async () => {
      toast.success('已指派角色')
      onOpenChange(false)
      setAssignmentId(crypto.randomUUID())
      setScopeType('')
      setScopeId('')
      await queryClient.invalidateQueries({ queryKey: queryKeys.auth.permissions })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>指派角色</DialogTitle>
          <DialogDescription>
            選擇要授予此帳號的角色。一般情況不需填寫適用範圍；若有全局限定再展開進階設定。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-muted-foreground text-xs font-medium">角色</label>
            <select className={selectClassName} value={roleCode} onChange={(e) => setRoleCode(e.target.value)}>
              <option value="">請選擇</option>
              {getRoleSelectOptions().map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <details className="rounded-md border border-border p-3 text-sm">
            <summary className="cursor-pointer font-medium text-foreground">進階設定（選填）</summary>
            <div className="mt-3 space-y-2">
              <p className="text-muted-foreground text-xs">
                僅在系統管理員指示下填寫；多數情境可留空。
              </p>
              <div>
                <label className="text-muted-foreground text-xs font-medium">適用範圍類型</label>
                <Input value={scopeType} onChange={(e) => setScopeType(e.target.value)} placeholder="例如：region" />
              </div>
              <div>
                <label className="text-muted-foreground text-xs font-medium">範圍識別</label>
                <Input value={scopeId} onChange={(e) => setScopeId(e.target.value)} />
              </div>
            </div>
          </details>
          <Button
            type="button"
            className="w-full"
            loading={mutation.isPending}
            disabled={!roleCode.trim()}
            onClick={() => mutation.mutate()}
          >
            確認指派
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
