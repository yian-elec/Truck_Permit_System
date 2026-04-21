import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { postSupplementResponseApi, type SupplementResponseBody } from '../api/post-supplement-response'

export function useSupplementResponse(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: SupplementResponseBody) =>
      postSupplementResponseApi(applicationId!, body),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.supplementRequests(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationDetail(applicationId),
      })
    },
  })
}
