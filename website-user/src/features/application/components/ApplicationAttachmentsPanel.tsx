import {
  AttachmentUploader,
  type SlotAttachment,
} from '@/features/attachment/components/AttachmentUploader'
import { SectionCard } from '@/shared/ui'

import { APPLICATION_ATTACHMENT_SLOTS } from '../constants/attachment-slots'

type Props = {
  applicationId: string
  attachments: unknown
}

function attachmentsForSlot(rawList: unknown, slotCode: string): SlotAttachment[] {
  if (!Array.isArray(rawList)) return []
  const out: SlotAttachment[] = []
  for (const item of rawList) {
    if (item === null || typeof item !== 'object') continue
    const a = item as Record<string, unknown>
    const attachment_id = a.attachment_id
    const attachment_type = a.attachment_type
    const original_filename = a.original_filename
    const uploaded_at = a.uploaded_at
    if (
      typeof attachment_id !== 'string' ||
      typeof attachment_type !== 'string' ||
      typeof original_filename !== 'string' ||
      typeof uploaded_at !== 'string' ||
      attachment_type !== slotCode
    ) {
      continue
    }
    out.push({ attachment_id, original_filename, uploaded_at })
  }
  return out.sort((x, y) => y.uploaded_at.localeCompare(x.uploaded_at))
}

export function ApplicationAttachmentsPanel({ applicationId, attachments }: Props) {
  const d = attachments as { attachments?: unknown }
  const list = d?.attachments ?? []

  return (
    <SectionCard
      title="附件上傳"
      description="每一項各上傳一格；必傳僅「行車執照影本」，其餘選傳。"
    >
      <div className="space-y-8">
        {APPLICATION_ATTACHMENT_SLOTS.map((slot) => {
          const slotAttachments = attachmentsForSlot(list, slot.code)
          return (
            <div
              key={slot.code}
              className="space-y-3 rounded-lg border border-border p-4"
            >
              <div>
                <p className="text-sm font-medium">
                  {slot.title}
                  {slot.required ? (
                    <span className="text-destructive"> *</span>
                  ) : (
                    <span className="text-muted-foreground"> （選填）</span>
                  )}
                </p>
                {slot.description ? (
                  <p className="mt-1 text-xs text-muted-foreground">{slot.description}</p>
                ) : null}
              </div>
              <AttachmentUploader
                applicationId={applicationId}
                attachmentType={slot.code}
                slotAttachments={slotAttachments}
              />
            </div>
          )
        })}
      </div>
    </SectionCard>
  )
}
