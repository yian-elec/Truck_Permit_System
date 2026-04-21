import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { deleteAttachmentApi } from '../api/delete-attachment'

export function useDeleteAttachment(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (attachmentId: string) => deleteAttachmentApi(applicationId!, attachmentId),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.attachments(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationDetail(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationEditModel(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.submissionCheck(applicationId),
      })
    },
  })
}
