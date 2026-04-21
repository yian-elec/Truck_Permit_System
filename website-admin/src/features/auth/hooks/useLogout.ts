import { useMutation, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/constants/query-keys'
import { logoutApi } from '../api/logout'
import { useAuthStore } from '../store/auth.store'

export function useLogout() {
  const queryClient = useQueryClient()
  const clearSession = useAuthStore((s) => s.clearSession)
  const sessionId = useAuthStore((s) => s.sessionId)

  return useMutation({
    mutationFn: async () => {
      if (sessionId) {
        await logoutApi(sessionId)
      }
    },
    onSettled: () => {
      clearSession()
      void queryClient.removeQueries({ queryKey: queryKeys.auth.me })
      void queryClient.removeQueries({ queryKey: queryKeys.auth.permissions })
    },
  })
}
