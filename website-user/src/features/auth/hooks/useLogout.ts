import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { queryKeys } from '@/shared/constants/query-keys'

import { logoutApi } from '../api/logout'
import { useAuthStore } from '../store/auth.store'

export function useLogout() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const clearSession = useAuthStore((s) => s.clearSession)

  return useMutation({
    mutationFn: logoutApi,
    onSettled: () => {
      clearSession()
      queryClient.removeQueries({ queryKey: queryKeys.auth.me })
      navigate(routePaths.login, { replace: true })
    },
  })
}
