import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getHandlingUnitsApi } from '../api/get-handling-units'

export function useHandlingUnits() {
  return useQuery({
    queryKey: queryKeys.publicService.handlingUnits,
    queryFn: getHandlingUnitsApi,
  })
}
