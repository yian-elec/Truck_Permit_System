import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { completeUploadApi, type CompleteUploadBody } from '../api/complete-upload'

export function useCompleteUpload(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: CompleteUploadBody) => completeUploadApi(applicationId!, body),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.attachments(applicationId),
      })
      // Checklist / is_satisfied lives on application detail, not the attachments list.
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
