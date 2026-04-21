import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { patchApplicationApi } from '../api/patch-application'
import type { PatchApplicationRequestBody } from '../types/application-dto.schema'

export function usePatchApplication(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: PatchApplicationRequestBody) =>
      patchApplicationApi(applicationId!, body),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationDetail(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.applicationEditModel(applicationId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.pageModel.applicationEditor(applicationId),
      })
    },
  })
}
