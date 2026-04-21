import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getMyApplicationsApi } from '../api/get-my-applications'

export function useMyApplications() {
  return useQuery({
    queryKey: queryKeys.applicant.applications,
    queryFn: getMyApplicationsApi,
  })
}
