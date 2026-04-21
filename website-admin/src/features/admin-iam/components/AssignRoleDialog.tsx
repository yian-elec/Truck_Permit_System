import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { Button, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, Input } from '@/shared/ui'

import { assignRole } from '../api/admin-iam-api'

type Props = {
  userId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

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
      await queryClient.invalidateQueries({ queryKey: queryKeys.auth.permissions })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>指派角色</DialogTitle>
          <DialogDescription>POST /api/v1/admin/users/&#123;userId&#125;/roles</DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-muted-foreground text-xs font-medium">role_code</label>
            <Input value={roleCode} onChange={(e) => setRoleCode(e.target.value)} />
          </div>
          <div>
            <label className="text-muted-foreground text-xs font-medium">assignment_id（新建 UUID）</label>
            <Input className="font-mono text-xs" value={assignmentId} onChange={(e) => setAssignmentId(e.target.value)} />
          </div>
          <div>
            <label className="text-muted-foreground text-xs font-medium">scope_type</label>
            <Input value={scopeType} onChange={(e) => setScopeType(e.target.value)} />
          </div>
          <div>
            <label className="text-muted-foreground text-xs font-medium">scope_id</label>
            <Input value={scopeId} onChange={(e) => setScopeId(e.target.value)} />
          </div>
          <Button type="button" className="w-full" loading={mutation.isPending} onClick={() => mutation.mutate()}>
            指派角色
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
