import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getApplicantHomeModelApi } from '../api/get-applicant-home-model'

export function useApplicantHomePageModel() {
  return useQuery({
    queryKey: queryKeys.pageModel.applicationHome,
    queryFn: getApplicantHomeModelApi,
  })
}
