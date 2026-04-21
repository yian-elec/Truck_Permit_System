import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getPermissionsApi } from '../api/get-permissions'
import { useAuthStore } from '../store/auth.store'

export function usePermissions() {
  const token = useAuthStore((s) => s.token)

  return useQuery({
    queryKey: queryKeys.auth.permissions,
    queryFn: getPermissionsApi,
    enabled: Boolean(token),
    staleTime: 60_000,
  })
}
