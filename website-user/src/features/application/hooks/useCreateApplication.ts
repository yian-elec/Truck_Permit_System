import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { createApplicationApi, type CreateApplicationBody } from '../api/create-application'

export function useCreateApplication() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: CreateApplicationBody) => createApplicationApi(body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.applicant.applications })
    },
  })
}
