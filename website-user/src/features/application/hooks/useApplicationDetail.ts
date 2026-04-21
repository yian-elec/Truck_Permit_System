import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getApplicationDetailApi } from '../api/get-application-detail'

export function useApplicationDetail(applicationId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.applicant.applicationDetail(applicationId ?? ''),
    queryFn: () => getApplicationDetailApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
