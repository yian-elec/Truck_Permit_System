import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getRoutePreviewApi, type RoutePreviewData } from '../api/get-route-preview'

export function useRoutePreview(applicationId: string | undefined) {
  return useQuery<RoutePreviewData | null>({
    queryKey: queryKeys.applicant.routePreview(applicationId ?? ''),
    queryFn: () => getRoutePreviewApi(applicationId!),
    enabled: Boolean(applicationId),
  })
}
