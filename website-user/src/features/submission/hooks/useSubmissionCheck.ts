import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getSubmissionCheckApi } from '../api/get-submission-check'

export function useSubmissionCheck(applicationId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.applicant.submissionCheck(applicationId ?? ''),
    queryFn: () => getSubmissionCheckApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
