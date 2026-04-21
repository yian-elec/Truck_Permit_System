import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { toast } from 'sonner'

import { queryKeys } from '@/shared/constants/query-keys'
import { ApiError } from '@/shared/api/api-error'
import { Button, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, Input } from '@/shared/ui'

import { overrideRoute } from '../api/route-api'

type Props = {
  applicationId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function OverrideRouteDialog({ applicationId, open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [wkt, setWkt] = useState('')
  const [reason, setReason] = useState('')
  const [baseCandidateId, setBaseCandidateId] = useState('')

  const mutation = useMutation({
    mutationFn: () =>
      overrideRoute(applicationId, {
        override_line_wkt: wkt,
        override_reason: reason,
        base_candidate_id: baseCandidateId.trim() || null,
      }),
    onSuccess: async () => {
      toast.success('已送出人工改線')
      onOpenChange(false)
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.routePlan(applicationId) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.review.ruleHits(applicationId) })
    },
    onError: (e) => toast.error(ApiError.fromUnknown(e).message),
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>人工改線</DialogTitle>
          <DialogDescription>以 WKT LINESTRING（WGS84）覆寫路線。</DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-muted-foreground text-xs font-medium">override_line_wkt</label>
            <textarea
              className="border-input bg-background mt-1 flex min-h-[100px] w-full rounded-md border px-3 py-2 font-mono text-xs"
              value={wkt}
              onChange={(e) => setWkt(e.target.value)}
              placeholder='LINESTRING (121.0 24.5, 121.1 24.6)'
            />
          </div>
          <div>
            <label className="text-muted-foreground text-xs font-medium">override_reason</label>
            <textarea
              className="border-input bg-background mt-1 flex min-h-[64px] w-full rounded-md border px-3 py-2 text-sm"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </div>
          <div>
            <label className="text-muted-foreground text-xs font-medium">base_candidate_id（選填）</label>
            <Input value={baseCandidateId} onChange={(e) => setBaseCandidateId(e.target.value)} className="font-mono" />
          </div>
          <Button type="button" className="w-full" loading={mutation.isPending} onClick={() => mutation.mutate()}>
            送出改線
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
