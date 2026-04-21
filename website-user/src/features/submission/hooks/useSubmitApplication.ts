import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { submitApplicationApi } from '../api/submit-application'

export function useSubmitApplication(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => submitApplicationApi(applicationId!),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationDetail(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.submissionCheck(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationTimeline(applicationId),
      })
    },
  })
}
