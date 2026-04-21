import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getAttachmentsApi } from '../api/get-attachments'

export function useAttachments(applicationId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.applicant.attachments(applicationId ?? ''),
    queryFn: () => getAttachmentsApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
