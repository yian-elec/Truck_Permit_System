import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'

import { getMeApi } from '../api/get-me'
import { useAuthStore } from '../store/auth.store'

export function useMe() {
  const token = useAuthStore((s) => s.token)
  const setUser = useAuthStore((s) => s.setUser)

  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: async () => {
      const user = await getMeApi()
      setUser(user)
      return user
    },
    enabled: Boolean(token),
  })
}
