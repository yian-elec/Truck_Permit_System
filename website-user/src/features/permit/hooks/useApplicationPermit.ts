import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getApplicationPermitApi } from '../api/get-application-permit'

export function useApplicationPermit(applicationId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.applicant.permit(applicationId ?? ''),
    queryFn: () => getApplicationPermitApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
