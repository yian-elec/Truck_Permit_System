import { useState } from 'react'
import { toast } from 'sonner'

import { formatDate } from '@/shared/utils/format-date'
import { ApiError } from '@/shared/api/api-error'
import { Button } from '@/shared/ui'

import { getAttachmentPreviewUrl } from '../api/review-attachment-api'

import { AttachmentPreviewDialog } from './AttachmentPreviewDialog'

export function AttachmentPreviewList({
  applicationId,
  attachments,
}: {
  applicationId: string
  attachments: Record<string, unknown>[]
}) {
  const [preview, setPreview] = useState<{ title: string; url: string } | null>(null)
  const [loadingId, setLoadingId] = useState<string | null>(null)

  async function openPreview(att: Record<string, unknown>) {
    const id = String(att.attachment_id ?? '')
    setLoadingId(id)
    try {
      const res = await getAttachmentPreviewUrl(applicationId, id)
      setPreview({ title: String(att.original_filename ?? '附件'), url: res.download_url })
    } catch (e) {
      toast.error(ApiError.fromUnknown(e).message)
    } finally {
      setLoadingId(null)
    }
  }

  if (attachments.length === 0) {
    return <p className="text-muted-foreground text-sm">無附件</p>
  }

  return (
    <>
      <ul className="divide-border divide-y rounded-md border">
        {attachments.map((a) => (
          <li
            key={String(a.attachment_id ?? '')}
            className="flex flex-wrap items-center justify-between gap-2 px-3 py-2 text-sm"
          >
            <div>
              <p className="font-medium">{String(a.original_filename ?? '')}</p>
              <p className="text-muted-foreground text-xs">
                {String(a.attachment_type ?? '')} ·{' '}
                {a.uploaded_at ? formatDate(String(a.uploaded_at)) : '—'}
              </p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              loading={loadingId === String(a.attachment_id ?? '')}
              onClick={() => void openPreview(a)}
            >
              預覽
            </Button>
          </li>
        ))}
      </ul>
      <AttachmentPreviewDialog
        open={preview != null}
        onOpenChange={(o) => !o && setPreview(null)}
        title={preview?.title ?? ''}
        url={preview?.url ?? null}
      />
    </>
  )
}
