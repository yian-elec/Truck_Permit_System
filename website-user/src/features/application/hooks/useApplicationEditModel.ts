import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getApplicationEditModelApi } from '../api/get-application-edit-model'

export function useApplicationEditModel(applicationId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.applicant.applicationEditModel(applicationId ?? ''),
    queryFn: () => getApplicationEditModelApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
