import { SectionCard } from '@/shared/ui'

import { AttachmentItem } from './AttachmentItem'

export function AttachmentList({
  applicationId,
  data,
}: {
  applicationId: string
  data: unknown
}) {
  const d = data as { attachments?: { attachment_id?: string; original_filename?: string }[] }
  const list = d?.attachments ?? []

  return (
    <SectionCard title="已上傳附件">
      {list.length === 0 ? (
        <p className="text-sm text-muted-foreground">尚無檔案。</p>
      ) : (
        <ul className="space-y-2">
          {list.map((a, i) => (
            <AttachmentItem
              key={a.attachment_id ?? i}
              applicationId={applicationId}
              attachmentId={a.attachment_id ?? String(i)}
              name={a.original_filename ?? '檔案'}
            />
          ))}
        </ul>
      )}
    </SectionCard>
  )
}
