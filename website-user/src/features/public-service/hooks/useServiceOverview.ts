import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getServiceOverviewApi } from '../api/get-service-overview'

export function useServiceOverview() {
  return useQuery({
    queryKey: queryKeys.publicService.overview,
    queryFn: getServiceOverviewApi,
  })
}
