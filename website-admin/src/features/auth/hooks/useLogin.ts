import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { storageKeys } from '@/shared/constants/storage-keys'
import { queryKeys } from '@/shared/constants/query-keys'
import { loginApi } from '../api/login'
import { useAuthStore } from '../store/auth.store'

export function useLogin() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setSession = useAuthStore((s) => s.setSession)

  return useMutation({
    mutationFn: loginApi,
    onSuccess: (data) => {
      if (data.mfa_required) {
        const cid = data.challenge_id
        if (cid) {
          try {
            sessionStorage.setItem(storageKeys.mfaChallengeId, cid)
          } catch {
            /* ignore */
          }
        }
        navigate(routePaths.mfa, {
          replace: true,
          state: { challengeId: cid ?? null },
        })
        return
      }
      const token = data.access_token
      if (!token) {
        return
      }
      const sid = data.session_id ?? null
      setSession(token, sid, null)
      void queryClient.invalidateQueries({ queryKey: queryKeys.auth.me })
      navigate(routePaths.adminHome, { replace: true })
    },
  })
}
