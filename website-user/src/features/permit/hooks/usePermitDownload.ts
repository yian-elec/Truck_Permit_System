import { useMutation } from '@tanstack/react-query'

import { downloadByUrl } from '@/shared/utils/download-by-url'

import { getPermitDownloadUrlApi } from '../api/get-permit-download-url'

export function usePermitDownload(applicationId: string | undefined) {
  return useMutation({
    mutationFn: async (documentId?: string) => {
      const res = await getPermitDownloadUrlApi(
        applicationId!,
        documentId ? { document_id: documentId } : {},
      )
      await downloadByUrl(res.download_url)
      return res
    },
  })
}
