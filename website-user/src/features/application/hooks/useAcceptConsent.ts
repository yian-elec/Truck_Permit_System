import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { acceptConsentApi } from '../api/accept-consent'

export function useAcceptConsent(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => acceptConsentApi(applicationId!),
    onSuccess: () => {
      if (!applicationId) return
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
