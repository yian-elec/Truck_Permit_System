import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getSupplementRequestsApi } from '../api/get-supplement-requests'

export function useSupplementRequests(applicationId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.applicant.supplementRequests(applicationId ?? ''),
    queryFn: () => getSupplementRequestsApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
