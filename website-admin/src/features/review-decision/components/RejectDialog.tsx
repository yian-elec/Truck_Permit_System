import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { Button, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/shared/ui'

import { rejectApplication } from '../api/review-decision-api'

type Props = {
  applicationId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function RejectDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [reason, setReason] = useState('')

  const mutation = useMutation({
    mutationFn: () => rejectApplication(applicationId, { reason }),
    onSuccess: async () => {
      toast.success('已駁回')
      onOpenChange(false)
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.caseDetail(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.tasks })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.decisions(applicationId) })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>駁回</DialogTitle>
          <DialogDescription>駁回申請並請填寫理由。</DialogDescription>
        </DialogHeader>
        <textarea
          className="border-input bg-background flex min-h-[120px] w-full rounded-md border px-3 py-2 text-sm"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="理由"
        />
        <Button type="button" variant="destructive" className="w-full" loading={mutation.isPending} onClick={() => mutation.mutate()}>
          確認駁回
        </Button>
      </DialogContent>
    </Dialog>
  )
}
