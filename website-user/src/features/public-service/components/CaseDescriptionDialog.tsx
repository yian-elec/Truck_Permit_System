import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui'

import { CaseDescriptionContent } from './CaseDescriptionContent'

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CaseDescriptionDialog({ open, onOpenChange }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-2xl overflow-y-auto p-0">
        <DialogHeader className="border-b border-border px-6 py-4">
          <DialogTitle>案件說明</DialogTitle>
          <DialogDescription>
            新北市政府警察局交通警察大隊辦理之大貨車臨時通行證相關資訊。
          </DialogDescription>
        </DialogHeader>
        <div className="px-6 py-4">
          <CaseDescriptionContent />
        </div>
      </DialogContent>
    </Dialog>
  )
}
