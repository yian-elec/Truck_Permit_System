import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { createRouteRequestApi, type RouteRequestBody } from '../api/create-route-request'

export function useCreateRouteRequest(applicationId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: RouteRequestBody) => createRouteRequestApi(applicationId!, body),
    onSuccess: () => {
      if (!applicationId) return
      void queryClient.invalidateQueries({
        queryKey: queryKeys.applicant.routePreview(applicationId),
      })
    },
  })
}
