import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui'

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  url: string | null
}

export function AttachmentPreviewDialog({ open, onOpenChange, title, url }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>若為圖片或 PDF，可直接於新分頁開啟下載連結。</DialogDescription>
        </DialogHeader>
        {url ? (
          <div className="space-y-2">
            <a
              href={url}
              target="_blank"
              rel="noreferrer"
              className="text-primary text-sm font-medium underline"
            >
              在新分頁開啟／下載
            </a>
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">無預覽 URL</p>
        )}
      </DialogContent>
    </Dialog>
  )
}
