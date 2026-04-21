import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { routePaths } from '@/shared/constants/route-paths'
import { queryKeys } from '@/shared/constants/query-keys'

import { loginApi, type LoginRequestBody } from '../api/login'
import { useAuthStore } from '../store/auth.store'

export function useLogin() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setSession = useAuthStore((s) => s.setSession)
  const setMfaChallenge = useAuthStore((s) => s.setMfaChallenge)

  return useMutation({
    mutationFn: (body: LoginRequestBody) => loginApi(body),
    onSuccess: (data) => {
      if (data.mfa_required) {
        const challengeId = data.challenge_id
        if (!challengeId) {
          console.error('MFA required but challenge_id missing from API')
          return
        }
        setMfaChallenge({
          challenge_id: challengeId,
          session_id: data.session_id ?? undefined,
        })
        navigate(routePaths.mfa, { replace: true })
        return
      }
      if (!data.access_token) {
        console.error('Login succeeded without access_token')
        return
      }
      setSession(data.access_token, null)
      void queryClient.invalidateQueries({ queryKey: queryKeys.auth.me })
      navigate(routePaths.applicant, { replace: true })
    },
  })
}
