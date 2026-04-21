import { useMutation } from '@tanstack/react-query'

import { downloadByUrl } from '@/shared/utils/download-by-url'

import { getAttachmentDownloadUrlApi } from '../api/get-attachment-download-url'

export function useAttachmentDownload(applicationId: string | undefined) {
  return useMutation({
    mutationFn: async (attachmentId: string) => {
      const res = await getAttachmentDownloadUrlApi(applicationId!, attachmentId)
      await downloadByUrl(res.download_url)
      return res
    },
  })
}
