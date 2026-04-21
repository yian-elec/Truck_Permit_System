import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getConsentLatestApi } from '../api/get-consent-latest'

export function useConsentLatest() {
  return useQuery({
    queryKey: queryKeys.publicService.consentLatest,
    queryFn: getConsentLatestApi,
  })
}
