import { useState } from 'react'
import { toast } from 'sonner'

import {
  env,
  getAttachmentBucketName,
  shouldSkipDirectUploadToStorage,
} from '@/shared/config/env'
import { Button, FileUpload } from '@/shared/ui'
import { formatFileSize } from '@/shared/utils/format-file-size'

import { useAttachmentDownload } from '../hooks/useAttachmentDownload'
import { useCompleteUpload } from '../hooks/useCompleteUpload'
import { useCreateUploadUrl } from '../hooks/useCreateUploadUrl'
import { useDeleteAttachment } from '../hooks/useDeleteAttachment'

async function sha256Hex(file: File): Promise<string> {
  const buf = await file.arrayBuffer()
  const hash = await crypto.subtle.digest('SHA-256', buf)
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

export type SlotAttachment = {
  attachment_id: string
  original_filename: string
  uploaded_at: string
}

export function AttachmentUploader({
  applicationId,
  attachmentType,
  slotAttachments,
}: {
  applicationId: string
  attachmentType: string
  slotAttachments: SlotAttachment[]
}) {
  const createUrl = useCreateUploadUrl(applicationId)
  const complete = useCompleteUpload(applicationId)
  const download = useAttachmentDownload(applicationId)
  const remove = useDeleteAttachment(applicationId)
  const [busy, setBusy] = useState(false)

  const hasFile = slotAttachments.length > 0
  const primary = hasFile ? slotAttachments[0] : null

  const disabled =
    busy || createUrl.isPending || complete.isPending || download.isPending || remove.isPending

  const deleteAllInSlot = async () => {
    for (const a of slotAttachments) {
      await remove.mutateAsync(a.attachment_id)
    }
  }

  const uploadFile = async (file: File) => {
    const mime = file.type || 'application/octet-stream'
    const up = await createUrl.mutateAsync({ mime_type: mime })

    const bucket = getAttachmentBucketName()
    const storageProvider = (env.VITE_ATTACHMENT_STORAGE_PROVIDER ?? 's3').trim()
    if (!bucket) {
      toast.error('未設定上傳儲存（正式環境請設定 VITE_ATTACHMENT_BUCKET_NAME）。')
      return
    }

    if (!shouldSkipDirectUploadToStorage(up.upload_url)) {
      const put = await fetch(up.upload_url, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': mime },
      })
      if (!put.ok) {
        throw new Error(`Storage PUT failed (${put.status})`)
      }
    }
    const checksum = await sha256Hex(file)
    const attachmentId = crypto.randomUUID()
    await complete.mutateAsync({
      file_id: up.file_id,
      attachment_id: attachmentId,
      attachment_type: attachmentType,
      original_filename: file.name,
      mime_type: mime,
      size_bytes: file.size,
      checksum_sha256: checksum,
      bucket_name: bucket,
      object_key: up.object_key,
      storage_provider: storageProvider,
    })
    toast.success(`已上傳 ${file.name}（${formatFileSize(file.size)}）`)
  }

  const handleFile = async (file: File) => {
    setBusy(true)
    try {
      if (slotAttachments.length > 0) {
        await deleteAllInSlot()
      }
      await uploadFile(file)
    } catch {
      toast.error('上傳失敗')
    } finally {
      setBusy(false)
    }
  }

  const handleDelete = async () => {
    setBusy(true)
    try {
      await deleteAllInSlot()
      toast.success('已刪除附件')
    } catch {
      toast.error('刪除失敗')
    } finally {
      setBusy(false)
    }
  }

  if (!hasFile || !primary) {
    return (
      <FileUpload
        accept="application/pdf,image/*"
        disabled={disabled}
        label="上傳檔案"
        onFile={handleFile}
      />
    )
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2 rounded-md border border-border p-3 text-sm">
        <span className="min-w-0 flex-1 truncate" title={primary.original_filename}>
          {primary.original_filename}
        </span>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            type="button"
            disabled={disabled}
            loading={download.isPending}
            onClick={() => download.mutate(primary.attachment_id)}
          >
            下載
          </Button>
          <Button
            size="sm"
            variant="destructive"
            type="button"
            disabled={disabled}
            loading={remove.isPending}
            onClick={() => void handleDelete()}
          >
            刪除
          </Button>
          <FileUpload
            accept="application/pdf,image/*"
            disabled={disabled}
            label="重新上傳"
            onFile={handleFile}
          />
        </div>
      </div>
    </div>
  )
}
