import { Button } from '@/shared/ui'

import { useAttachmentDownload } from '../hooks/useAttachmentDownload'
import { useDeleteAttachment } from '../hooks/useDeleteAttachment'

export function AttachmentItem({
  applicationId,
  attachmentId,
  name,
}: {
  applicationId: string
  attachmentId: string
  name: string
}) {
  const download = useAttachmentDownload(applicationId)
  const remove = useDeleteAttachment(applicationId)

  return (
    <li className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border p-2 text-sm">
      <span>{name}</span>
      <div className="flex gap-2">
        <Button
          size="sm"
          variant="outline"
          type="button"
          loading={download.isPending}
          onClick={() => download.mutate(attachmentId)}
        >
          下載
        </Button>
        <Button
          size="sm"
          variant="destructive"
          type="button"
          loading={remove.isPending}
          onClick={() => remove.mutate(attachmentId)}
        >
          刪除
        </Button>
      </div>
    </li>
  )
}
