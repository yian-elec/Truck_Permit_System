import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { queryKeys } from '@/shared/constants/query-keys'
import { routePaths } from '@/shared/constants/route-paths'
import { storageKeys } from '@/shared/constants/storage-keys'

import { mfaVerifyApi } from '../api/mfa-verify'
import { useAuthStore } from '../store/auth.store'

export function useMfaVerify() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setSession = useAuthStore((s) => s.setSession)

  return useMutation({
    mutationFn: mfaVerifyApi,
    onSuccess: (data) => {
      try {
        sessionStorage.removeItem(storageKeys.mfaChallengeId)
      } catch {
        /* ignore */
      }
      const token = data.access_token
      const sid = data.session_id ?? null
      setSession(token, sid, null)
      void queryClient.invalidateQueries({ queryKey: queryKeys.auth.me })
      navigate(routePaths.adminHome, { replace: true })
    },
  })
}
