import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getTimelineApi } from '../api/get-timeline'

export function useTimeline(applicationId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.applicant.applicationTimeline(applicationId ?? ''),
    queryFn: () => getTimelineApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
