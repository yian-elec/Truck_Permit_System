import { useState } from 'react'
import { toast } from 'sonner'

import { getErrorMessage } from '@/shared/api/api-error'
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  SectionCard,
} from '@/shared/ui'

import type { useAcceptConsent } from '../hooks/useAcceptConsent'

type Props = {
  consent: ReturnType<typeof useAcceptConsent>
}

export function ConsentClauseSection({ consent }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <SectionCard title="同意條款">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button type="button" variant="secondary">
            閱讀同意條款
          </Button>
        </DialogTrigger>
        <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>同意條款</DialogTitle>
            <DialogDescription className="sr-only">
              請閱讀以下條款後，點選本人同意以完成記錄。
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 text-left text-sm text-foreground">
            <p className="whitespace-pre-wrap leading-relaxed">
              本人　　辦理「 申請大貨車臨時通行證 」業務，並同意由新北市政府代為查驗申請人之資料。
            </p>
            <p className="text-right">此致</p>
            <p className="font-medium">新北市政府</p>
          </div>
          <Button
            type="button"
            className="w-full"
            loading={consent.isPending}
            onClick={() =>
              consent.mutate(undefined, {
                onSuccess: () => {
                  toast.success('已記錄同意')
                  setOpen(false)
                },
                onError: (e) => toast.error(getErrorMessage(e)),
              })
            }
          >
            本人同意
          </Button>
        </DialogContent>
      </Dialog>
    </SectionCard>
  )
}
